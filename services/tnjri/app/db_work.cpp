connection Conn("dbname = db user = username password = password host = db port = 5432");
const string default_tree_str = "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 "
                                "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 "
                                "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0";

bool init_db() {
    if (!Conn.is_open())
        return 0;
    string sql = "CREATE TABLE IF NOT EXISTS Users("  \
                  "id SERIAL PRIMARY KEY," \
                  "username TEXT," \
                  "password TEXT," \
                  "tree TEXT," \
                  "encryption_key TEXT," \
                  "encrypted TEXT);";
    work W(Conn);
    W.exec(sql);
    W.commit();
    return 1;
}

int login_user(const string &login, const string &password) {
    work W(Conn);
    params p;
    p.reserve(2);
    p.append(login);
    p.append(password);
    auto R = W.exec_params("SELECT id FROM Users WHERE username = $1 and password = $2", p);
    return R.empty() ? -1 : R.begin()[0].as<int>();
}

int get_userid(const string &login) {
    work W(Conn);
    params p;
    p.reserve(1);
    p.append(login);
    auto R = W.exec_params("SELECT id FROM Users WHERE username = $1", p);
    return R.empty() ? -1 : R.begin()[0].as<int>();
}

void register_user(const string &login, const string &password) {
    work W(Conn);
    params p;
    p.reserve(4);
    p.append(login);
    p.append(password);
    p.append(default_tree_str);
    p.append("");
    W.exec_params("INSERT INTO Users (username,password,tree,encryption_key,encrypted) VALUES ($1, $2, $3, $4, '')", p);
    W.commit();
}

pair <vector<int>, string> get_tree_state(int id) {
    work W(Conn);
    params p;
    p.reserve(1);
    p.append(id);
    auto R = W.exec_params("SELECT tree, encrypted FROM Users WHERE id = $1", p);
    pair <vector<int>, string> result;
    string tree_str;
    if (!R.empty()) {
        tree_str = R.begin()[0].as<string>();
        result.second = R.begin()[1].as<string>();
    } else {
        tree_str = default_tree_str;
        result.second = "";
    }
    istringstream iss(tree_str);
    for (int s; iss >> s;)
        result.first.push_back(s);
    return result;
}

string get_key_state(int id) {
    work W(Conn);
    params p;
    p.reserve(1);
    p.append(id);
    auto R = W.exec_params("SELECT encryption_key FROM Users WHERE id = $1", p);
    return R.empty() ? "" : R.begin()[0].as<string>();
}

void set_tree_state(const string &login, array<unsigned int, 128> tree, string encrypted) {
    stringstream iss;
    for (int i = 1; i < tree.size(); i++)
        iss << tree[i] << " ";
    work W(Conn);
    params p;
    p.reserve(3);
    p.append(iss.str());
    p.append(encrypted);
    p.append(login);
    W.exec_params("UPDATE Users SET tree = $1::text, encrypted = $2::text WHERE username = $3::text", p);
    W.commit();
}

void set_key_state(const string &login, const string &str_key) {
    work W(Conn);
    params p;
    p.reserve(2);
    p.append(str_key);
    p.append(login);
    W.exec_params("UPDATE Users SET encryption_key = $1::text WHERE username = $2::text", p);
    W.commit();
}