# InnoCTF 2022 Final (Attack Defense)

В `./geth` находится вся инфа по запуску блокчейна и сервисов, которые его используют. Остальные сервисы запускаются стандартно: `docker-compose up`

## Уязвимости

В основном описаны словами, для некоторых есть эксплоиты в `./exploits`

### shashlik

0) Идентичный секретный токен для всех 
1) Приватные треды не реализованы - любой может читать чужие треды, они даже отображаются в gui
2) Любой может сбросить пароль другого пользователя (по параметру username)
3) Переполнение буфера в бинарнике проверки сложности пароля (см. эксплойт `shashlik_1.py`)

### tnjri

`./exploits/tnjri.cpp`

0) IDOR + Небезопасное генерирование seed. В ручке /api/state/tree присутствовал IDOR, который позволял читать чужие сохраненные стейты зашифрованных деревьев.
Id пользователей были autoincrement, что позволяло получать деревья предыдущих пользователей.
Для расшифровки сообщений на дереве надо было понять как шифруется сообщение. Используется дерево отрезков с множественными операциями на дереве
http://e-maxx.ru/algo/segment_tree
Для генерирования ключа в функции gen_key небезопасно создавался ключ на основе введенной строки.
Битовые сдвиги в конце функции обнуляли первые 16 бит, что позволяло перебрать все варианты ключа и сбрутить правильный.
Для шифрования 1000 раз генерировались случайные параметры l, r, v и вызывался xor на дереве отрезков для элементов с l по r значением v.
Эксплойт для брута приведен ниже.
Для фикса возможно было увеличить количество итераций с 1000 до 100000, чтобы усложнить брут.

1) В api ручке /about?name=<login> при указании длинного параметра login выдавалась пустая страница. Если посмотреть логи, которые писались в log.txt, можно было обнаружить ошибки "Template xxx not found", где xxx - это часть параметра login с определенной позиции.
Даже без реверса бинаря можно понять, что подав строку ../log.txt в параметр name и добив нужным количеством символом в начале, можно прочитать файл log.txt.
В этот файл писались plaintext строки еще до их шифрования.
Для фикса можно было уменьшить третий параметр функции strncat в обработке ручки /about или просто отключить логи в entry.sh.

### smartchat-contract

0) Изначально стоит плохой способ шифрования сообщений, который берется из cli клиента. Эксплойт `smartchat_1.py`. Для фикса нужно передеплоить контракт с любым алгоритмом из `INTERNAL1/INTERNAL2/EXTERNAL`
1) Race condition при создании комнаты, поскольку нет проверки того, что комната уже существует. Можно мониторить блокчейн на наличие новых комнат, созданных чекером, брать название комнаты и адрес чекера, создавать свою комнату, в которую нужно добавить чекер и изменить алгоритм комнаты на небезопасный, что открывает первую уязвимость, если она уже закрыта. Возможно, поскольку после создания комнаты чекер ждет некоторое время (видно в `lib.py`)
2) Если поднимать контракт на блокчейне, где не нужно заранее инициализировать используемые кошельки, то открываются еще уязвимости на брутфорс кошелька босса (адрес должен начинаться с 0x31337) и замену алгоритмов комнат на небезопасные. Реализацию мультипоточного брутфорса можно найти в `exploits/smartchat_2.py` (с 7 потоками находится подходящий кошелек за ~20 мин). Для тестов можно использовать блокчейн ganache, либо публичные тестнеты BSC testnet/Ropsten/и т.д.

### smartchat-web

0) Можно читать сообщения по названию комнаты (имена комнат можно получить из блокчейна)
1) Сеансы cookie зависят от временной метки (эта уязвимость детально не тестировалась, но вроде должна работать :D)
