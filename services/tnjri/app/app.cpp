#include <string>
#include <map>

#include <pqxx/pqxx>
#include "crow.h"

using namespace std;
using namespace pqxx;

#include "tree.cpp"
#include "db_work.cpp"

#define N 64
#define ITERATIONS 1000

// generate pseudo random numeric key based on string key
int gen_key(const string& key_str){
    int ret = 1e7;
    // xor with multiplied symbols
    for (auto c: key_str) {
        ret ^= c;
        ret ^= (c * 2) << 2;
        ret ^= (c * 4) << 4;
        ret ^= (c * 8) << 8;
        ret ^= (c * 16) << 16;
    }
    // xor and add more numbers
    for (int i = 0; i < 50; i++) {
        for (auto c: key_str) {
            ret *= c;
            ret += i;
            ret ^= 0xBEEF;
            ret = ret >> 2;
        }
    }
    // make cycle shifts and xor
    ret ^= ret % 8;
    ret = ret >> 2;
    ret ^= ret % 8;
    ret = ret << 4;
    ret ^= ret % 8;
    ret = ret >> 8;
    ret ^= ret % 8;
    ret = ret << 16;
    ret ^= ret % 8;
    if (ret < 0) ret *= -1;
    return ret;
}

string encrypt(const string& login, string data, const string& str_key){
    array<unsigned int, 128> tmp_tree = {};
    build_tree(1, 0, N-1, std::move(data), tmp_tree);
    set_key_state(login, str_key);
    int ikey = gen_key(str_key);
    srand(ikey);
    for (int i = 0; i < ITERATIONS; i++){
        int l = rand() % N;
        int r = rand() % N;
        if (r < l) swap(l, r);
        int v = rand() % 127;
        update_tree(1, 0, N-1, l, r, v, tmp_tree);
    }
    string encrypted = "";
    traverse_tree(1, 0, N-1, 0, tmp_tree, encrypted);
    string b64encoded = crow::utility::base64encode(encrypted, encrypted.size());
    set_tree_state(login, tmp_tree, b64encoded);
    return b64encoded;
}

pair<string, vector<int>> decrypt(const string& data, const string& str_key){
    array<unsigned int, 128> tmp_tree = {};
    string decoded = crow::utility::base64decode(data, data.size());
    build_tree(1, 0, N-1, decoded, tmp_tree);
    srand(gen_key(str_key));
    for (int i = 0; i < ITERATIONS; i++){
        int l = rand() % N;
        int r = rand() % N;
        if (r < l) swap(l, r);
        int v = rand() % 127;
        update_tree(1, 0, N-1, l, r, v, tmp_tree);
    }
    string plain = "";
    pair<string, vector<int>> ret;
    traverse_tree(1, 0, N-1, 0, tmp_tree, plain);
    ret.second = vector<int>(tmp_tree.begin() + 1, tmp_tree.end());
    ret.first = plain;
    return ret;
}

void logrotate(){
    while(1) {
        system("/bin/bash -c 'if [[ $(find /app/log.txt -type f -size +1M) ]]; then cp /app/log.txt /app/old.txt; : > /app/log.txt; fi'");
        sleep(60 * 5); // 5 minutes
    }
}

int main(){
    crow::SimpleApp app;

    if (!init_db()){
        CROW_LOG_WARNING << "Can't open database";
        return 1;
    }

    //templates

    CROW_ROUTE(app, "/")
    ([](const crow::request&, crow::response& res) {
        char load_html[32] = "templates/login.html";
        res.set_static_file_info(load_html);
        res.end();
    });

    CROW_ROUTE(app, "/register")
    ([](const crow::request&, crow::response& res) {
        char load_html[32] = "templates/register.html";
        res.set_static_file_info(load_html);
        res.end();
    });

    CROW_ROUTE(app, "/encrypt")
    ([](const crow::request&, crow::response& res) {
        char load_html[32] = "templates/encrypt.html";
        res.set_static_file_info(load_html);
        res.end();
    });

    CROW_ROUTE(app, "/decrypt")
    ([](const crow::request&, crow::response& res) {
        char load_html[32] = "templates/decrypt.html";
        res.set_static_file_info(load_html);
        res.end();
    });

    CROW_ROUTE(app, "/about")
    ([] (const crow::request& req){
        char welcome[32] = "Welcome,  ";
        char load_html[32] = "about.html";
        crow::mustache::context ctx;
        const char* name = req.url_params.get("name") ? req.url_params.get("name") : "Anonym";
        strncat(welcome, name, 32);
        ctx["welcome"] = welcome;
        return crow::mustache::load_unsafe(load_html).render(ctx);
    });

    //api

    app.route_dynamic("/api/login")
    .methods("POST"_method)
    ([](const crow::request& req){
        auto x = crow::json::load(req.body);
        crow::json::wvalue json_res;
        if (!x){
            json_res["status"] = "Json error";
            return crow::response(400, json_res);
        }
        auto login = x["login"].s(), password = x["passwd"].s();
        int id = login_user(login, password);
        if (id < 0){
            json_res["status"] = "Wrong credentials";
            return crow::response(403, json_res);
        }
        json_res["id"] = id;
        CROW_LOG_WARNING << "Successful login for " << login;
        return crow::response(200, json_res);
    });

    CROW_ROUTE(app, "/api/register")
    .methods("POST"_method)
    ([](const crow::request& req){
        auto x = crow::json::load(req.body);
        crow::json::wvalue json_res;
        if (!x){
            json_res["status"] = "Json error";
            return crow::response(400, json_res);
        }
        auto login = x["login"].s(), password = x["passwd"].s();
        if (get_userid(login) >= 0){
            json_res["status"] = "Users exists";
            return crow::response(409, json_res);
        }
        register_user(login, password);
        json_res["status"] = "ok";
        CROW_LOG_WARNING << "Registered user " << login;
        return crow::response(201, json_res);
    });

    CROW_ROUTE(app, "/api/encrypt")
    .methods("POST"_method)
    ([](const crow::request& req){
        auto json_req = crow::json::load(req.body);
        crow::json::wvalue json_res;
        if (!json_req){
            json_res["status"] = "Json error";
            return crow::response(400, json_res);
        }
        string login = json_req["login"].s(), password = json_req["passwd"].s(), data = json_req["data"].s(), str_key = json_req["key"].s();
        if (login_user(login, password) < 0){
            json_res["status"] = "Login error";
            return crow::response(403, json_res);
        }
        string encrypted = encrypt(login, data, str_key);
        CROW_LOG_WARNING << "Encrypted " << data << " for " << login;
        json_res["encrypted"] = encrypted;
        return crow::response(200, json_res);
    });

    CROW_ROUTE(app, "/api/decrypt")
    .methods("POST"_method)
    ([](const crow::request& req){
        auto json_req = crow::json::load(req.body);
        crow::json::wvalue json_res;
        if (!json_req){
            json_res["status"] = "Json error";
            return crow::response(400, json_res);
        }
        string login = json_req["login"].s(), password = json_req["passwd"].s(), data = json_req["data"].s(), str_key = json_req["key"].s();
        if (login_user(login, password) < 0){
            json_res["status"] = "Login error";
            return crow::response(403, json_res);
        }
        auto val = decrypt(data, str_key);
        json_res["decrypted"] = val.first;
        json_res["tree"] = val.second;
        CROW_LOG_WARNING << "Decrypted " << data << " for " << login;
        return crow::response(200, json_res);
    });

    CROW_ROUTE(app, "/api/state/tree")
    .methods("POST"_method)
    ([](const crow::request& req){
        auto json_req = crow::json::load(req.body);
        crow::json::wvalue json_res;
        if (!json_req){
            json_res["status"] = "Json error";
            return crow::response(400, json_res);
        }
        string login = json_req["login"].s(), password = json_req["passwd"].s();
        int id = (int)json_req["id"].i();
        if (login_user(login, password) < 0){
            json_res["status"] = "Login error";
            return crow::response(403, json_res);
        }
        auto result = get_tree_state(id);
        json_res["tree"] = result.first;
        json_res["encrypted"] = result.second;
        return crow::response(200, json_res);
    });

    CROW_ROUTE(app, "/api/state/key")
    .methods("POST"_method)
    ([](const crow::request& req){
        auto json_req = crow::json::load(req.body);
        crow::json::wvalue json_res;
        if (!json_req){
            json_res["status"] = "Json error";
            return crow::response(400, json_res);
        }
        string login = json_req["login"].s(), password = json_req["passwd"].s();
        int id = (int)json_req["id"].i();
        if (login_user(login, password) < 0 || get_userid(login) != id){
            json_res["status"] = "Login error";
            return crow::response(403, json_res);
        }
        json_res["key"] = get_key_state(id);
        return crow::response(200, json_res);
    });

    thread logrotate_thread(logrotate);
    app.loglevel(crow::LogLevel::Warning);
    CROW_LOG_WARNING << "Starting server";
    app.port(5000).run();
}
