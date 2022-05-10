import sys
from app import app, db

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'initdb':
            db.drop_all()
            db.create_all()
            db.session.commit()
            exit()
        else:
            print('[!] Unknown command!')
            exit(-1)
    app.run(debug=True, host='0.0.0.0')
