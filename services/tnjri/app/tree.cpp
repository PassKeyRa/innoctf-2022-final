void build_tree(int node, int a, int b, std::string data, std::array<unsigned int, 128> &tree) {
    if (a > b) return;
    if (a == b) {
        tree[node] = a < data.length() ? data[a] : 0;
        return;
    }
    build_tree(node * 2, a, (a + b) / 2, data, tree);
    build_tree(node * 2 + 1, 1 + (a + b) / 2, b, data, tree);
    tree[node] = 0;
}

void update_tree(int node, int a, int b, int i, int j, unsigned int value, std::array<unsigned int, 128> &tree) {
    if (a > b || a > j || b < i)
        return;
    if (a >= i && b <= j) {
        tree[node] ^= value;
        return;
    }
    tree[node * 2] ^= tree[node];
    tree[node * 2 + 1] ^= tree[node];
    tree[node] = 0;
    update_tree(node * 2, a, (a + b) / 2, i, j, value, tree);
    update_tree(1 + node * 2, 1 + (a + b) / 2, b, i, j, value, tree);
}

void traverse_tree(int node, int a, int b, unsigned int value, std::array<unsigned int, 128> &tree, std::string &encrypted) {
    if (a > b) return;
    if (a == b) {
        tree[node] ^= value;
        encrypted += (char) tree[node];
        return;
    }
    unsigned int xor_value = value ^ tree[node];
    traverse_tree(node * 2, a, (a + b) / 2, xor_value, tree, encrypted);
    traverse_tree(node * 2 + 1, 1 + (a + b) / 2, b, xor_value, tree, encrypted);
}
