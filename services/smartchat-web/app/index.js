const express = require('express')
const fs = require('fs')
const app = express()
const bodyParser = require('body-parser')
const hbs = require('express-hbs')
const morgan = require('morgan')
const cookieParser = require('cookie-parser')
const crypto = require('crypto')
const session = require('express-session')
const redis = require('redis')
const connectRedis = require('connect-redis')
const redisStorage = connectRedis(session)
const postgre = require('./postgre')
const SmartChat = require('./lib')

;(async function(){
	await postgre.createUsersTable();
	await postgre.createRoomsTable();
})()

const client = redis.createClient({
	host: process.env.REDIS_HOST || 'redis'
});
app.use(morgan('dev'))

var PORT = process.env.PORT || 8000
var BIND_ADDR = process.env.BIND_ADDR || '0.0.0.0'
var REDIS_HOST = process.env.REDIS_HOST || 'redis'
var REDIS_PORT = process.env.REDIS_PORT || 6379
var RPC_URL = process.env.RPC_URL || 'http://10.10.10.13:8545'
var CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS
var PRIVATE_KEY = fs.readFileSync(".secret", 'utf-8');

;(async function() { await SmartChat.init(RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS)})()

app.engine('hbs', hbs.express4({}))
app.use(bodyParser.json())
app.use(cookieParser())
app.set('views', './public')
app.set('view engine', 'hbs')
app.use("/css", express.static(__dirname + "/public/css"))
app.use("/img", express.static(__dirname + "/public/img"))
app.use("/js", express.static(__dirname + "/public/js"))
app.use('/',
	session({
		store: new redisStorage({
			host: REDIS_HOST,
			port: REDIS_PORT,
			client: client
		}),
		keys: ['key', 'user'],
		secret: 'UserKey',
		resave: true,
		saveUninitialized: true,
		cookie: {
			httpOnly: false
		}
	})
)

async function checkCorrectUser(req, res, next){
	try{
		if (req.session.key){
			var users = await postgre.getUserByName(req.session.user);
			if (users.length != 0){
				next()
			}
			else{
				res.status(403).redirect('/login')
			}
		}
		else{
			res.status(403).redirect('/login')
		}
	} catch (error) {
		console.log(error)
		res.status(403).redirect('/login')
	}
}

function getRandomInt(max) {
	return Math.floor(Math.random() * Math.floor(max));
}

// ---------- User space ----------
app.get('/', function(req, res, next){
	res.render('index.hbs', {'page-title':'Index'})
})

app.get('/login', function(req, res, next){
	res.render('login.hbs', {'page-title':'Login'})
})

app.get('/register', function(req, res, next){
	res.render('reg.hbs', {'page-title':'Register'})
})

app.get('/home', checkCorrectUser, async function(req, res, next){
	var users = await postgre.getUserByName(req.session.user);
	var userid = users[0].userid;
	var rooms = await postgre.getRoomsByUserid(userid)
	res.render('home.hbs', {'page-title':'Home', 'username':req.session.user, 'contract_address': CONTRACT_ADDRESS, 'rooms':rooms})
})

app.get('/chat', checkCorrectUser, async function(req, res, next){
	var roomname = req.query.roomname;
	try{
		var rooms = await postgre.getRoomByName(roomname);
		if (rooms.length == 0) {
			res.send({'error':'No such room!'})
		} else {
			var users = await postgre.getUserByName(req.session.user);
			if (users[0].userid != rooms[0].userid){
				res.send({'error':'No permissions!'}) 
			} else {
				var encryption_key = rooms[0].encryption_key
				var contract_address = rooms[0].contract_address
				messages = await SmartChat.getMessages(contract_address, encryption_key)
				res.render('chat.hbs', {'page-title':'Chat', 
					'roomname':roomname, 
					'messages':messages,
					'username':req.session.user})
			}
		}
	} catch (error) {
		console.log(error)
		res.status(403).send({'error':'Something went wrong'})
	}
})

app.get('/logout', async function(req, res){
	try {
		if (req.session.adminkey) {
			delete req.session.key
			delete req.session.user
			res.redirect('/login')
		} else {
	        	req.session.destroy(function(err){
				if(err){
					console.log(err);
					res.sendStatus(418);
				} else {
					res.redirect('/login');
				}
		 	});
		}
	} catch (e) {
		res.sendStatus(418);
	}
})

// ---------- API ----------

app.post('/api/login', async function(req, res){
	try{
		var { username, password } = req.body
		var users = await postgre.getUserByNamePass(username, password)
		if (users.length != 0){
			req.session.key = Math.floor(Date.now()/1000);
			req.session.user = users[0].username;
			res.json({'status':'ok', 'redirect':'/home'})
		} else {
			res.status(403).json({'error':'Try again!'})
		}	
	} catch (error) {
		res.status(403).json({'error':'Try again!'})
	}
})

app.post('/api/register', async function(req, res){
	var { username, password1, password2 } = req.body
	if (password1 == password2) {
		var users = await postgre.getUserByName(username)
		if (users.length != 0) {
			res.send({'error':'Username already exists'})
		} else {
			await postgre.setUser(username, password1)
			req.session.key = Math.floor(Date.now()/1000);
			req.session.user = username;
			res.send({'status':'ok', 'redirect':'/'})
		}
	} else {
		res.status(403).send({'error':'Passwords don\'t match'})
	}
})

app.post('/api/createroom', async function(req, res){
	var { roomname } = req.body
	try{
		var users = await postgre.getUserByName(req.session.user);
		var userid = users[0].userid;
		var rooms = await postgre.getRoomByName(roomname);
		if (rooms.length != 0) {
			res.send({'error':'Room already exists'})
		} else {
			var encryption_key = crypto.randomBytes(16).toString('hex') //'12345678901234567890123456789012'
			await SmartChat.createRoom(roomname)
			contract_address = await SmartChat.getRoomByName(roomname)
			//console.log(contract_address, roomname)
			//console.log(await SmartChat.getMessages(contract_address))

			await postgre.setRoom(roomname, userid, contract_address, encryption_key)
			res.json({'status':'ok'})
		}
	} catch (error) {
		res.status(403).send({'error':'Something went wrong'})
	}
})

app.get('/api/getrooms', async function(req, res){
	try{
		var users = await postgre.getUserByName(req.session.user);
		var userid = users[0].userid;
		var rooms = await postgre.getRoomsByUserid(userid)
		res.json(rooms)
	} catch (error) {
		res.status(403).send({'error':'Something went wrong'})
	}
})

app.get('/api/getmessages', async function(req, res){
	var roomname = req.query.roomname;
	try{
		var rooms = await postgre.getRoomByName(roomname);
		if (rooms.length == 0) {
			res.send({'error':'No such room!'})
		} else {
			var encryption_key = rooms[0].encryption_key
			var contract_address = rooms[0].contract_address
			//console.log("Get from " + contract_address);
			res.json(await SmartChat.getMessages(contract_address, encryption_key))
			//res.json([{'author':'pidor', 'content':'ya pidoras'},{'author':'test', 'content':'ok ok'}])
		}
	} catch (error) {
    console.log(error)
		res.status(403).send({'error':'Something went wrong'})
	}
})

app.post('/api/sendmessage', async function(req, res){
	var { roomname, message } = req.body;
	try {
		var rooms = await postgre.getRoomByName(roomname);
		if (rooms.length == 0) {
			res.send({'error':'No such room!'})
		} else {
			var encryption_key = rooms[0].encryption_key
			var contract_address = rooms[0].contract_address
			var username = req.session.user

			// send to contract ????

			await SmartChat.newMessage(contract_address, message, encryption_key);

			res.json({'status':'ok'})
		}
	} catch (error) {
		res.status(403).send({'error':'Something went wrong'})
	}
})

app.get('/api/usersonline', async function(req, res){
	try {
		var users = []
		client.keys('*', async function(err, keys) {
			client.mget(keys, async function(err, values){
				if(err){console.log(err)}
				res.json(Array.prototype.map.call(values, (x) => JSON.parse(x).user))
			});
		})
	} catch (error) {
		console.log(error)
		res.status(403).send({'error':'Something went wrong'})
	}
})

// ---------- Admin space ----------

app.listen(PORT, BIND_ADDR, () => {
	console.log('Running on ' + BIND_ADDR + ':' + PORT)
})
