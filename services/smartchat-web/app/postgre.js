const Pool = require('pg').Pool
const POSTGRES_HOST = process.env.POSTGRES_HOST || 'postgres'
const POSTGRES_PORT = process.env.POSTGRES_PORT || 5432
const POSTGRES_USER = process.env.POSTGRES_USER || 'db_admin'
const POSTGRES_DBNAME = process.env.POSTGRES_DBNAME || 'chat_db'
const POSTGRES_PASS = process.env.POSTGRES_PASS || 'n4pW6BNkhJbbQVPA'

const pool = new Pool({
	user: POSTGRES_USER,
	host: POSTGRES_HOST,
	database: POSTGRES_DBNAME,
	password: POSTGRES_PASS,
	port: POSTGRES_PORT,
})


const createUsersTable = async () => {
	const client = await pool.connect()
	try {
		await client.query('CREATE TABLE IF NOT EXISTS users (userid SERIAL UNIQUE, username varchar(50) NOT NULL, password varchar(50) NOT NULL, PRIMARY KEY (userid), UNIQUE(username))')
	} catch (e){
		console.log(e.stack)
	} finally {
		client.release()
	}
}

const createRoomsTable = async () => {
	const client = await pool.connect()
	try {
		await client.query('CREATE TABLE IF NOT EXISTS rooms (roomid SERIAL UNIQUE, roomname varchar(50) NOT NULL UNIQUE, userid int NOT NULL, contract_address varchar(42) NOT NULL, encryption_key varchar(48), PRIMARY KEY (roomid), FOREIGN KEY (userid) REFERENCES users(userid) ON DELETE CASCADE)')
	} catch (e){
		console.log(e.stack)
	} finally {
		client.release()
	}
}

const setRoom = async (roomname, userid, contract_address, encryption_key) => {
	const client = await pool.connect()
	try {
		await client.query('INSERT INTO rooms (roomname, userid, contract_address, encryption_key) VALUES ($1, $2, $3, $4)', [roomname, userid, contract_address, encryption_key])
	} catch (e){
		console.log(e.stack)
	} finally {
		client.release()
	}
}

const setUser = async (username, password) => {
	const client = await pool.connect()
	try {
		await client.query('INSERT INTO users (username, password) VALUES ($1, $2)', [username, password])
	} catch (e){
		console.log(e.stack)
	} finally {
		client.release()
	}
}

const getRoomsByUserid = async function(userid){	
	const client = await pool.connect()
	var res
	try {
		res = await client.query('SELECT * FROM rooms WHERE userid=$1', [userid])
	} catch (e) {
		console.log(e.stack)
	} finally {
		client.release()
	}
	return res.rows
}

const getRoomByName = async function(roomname){
	const client = await pool.connect()
	var res
	try {
		res = await client.query('SELECT * FROM rooms WHERE roomname=$1', [roomname])
	} catch (e) {
		console.log(e.stack)
	} finally {
		client.release()
	}
	return res.rows
}
const getUserByName = async function(username){
	const client = await pool.connect()
	var res
	try {
		res = await client.query('SELECT * FROM users WHERE username=$1', [username])
	} catch (e) {
		console.log(e.stack)
	} finally {
		client.release()
	}
	return res.rows
}

const getUserByNamePass = async function(username, password){
        const client = await pool.connect()
        var res
        try {
                res = await client.query('SELECT * FROM users WHERE username=$1 AND password=$2', [username, password])
        } catch (e) {
                console.log(e.stack)
        } finally {
                client.release()
        }
        return res.rows
}

const getUserById = async function(id){
        const client = await pool.connect()
        var res
        try {
                res = await client.query('SELECT * FROM users WHERE userid=$1',[id])
        } catch (e) {
                console.log(e.stack)
        } finally {
                client.release()
        }
        return res.rows
}

module.exports = {
	createUsersTable,
	createRoomsTable,
	setRoom,
	setUser,
	getUserByName,
	getUserByNamePass,
	getRoomsByUserid,
	getRoomByName,
	getUserById
}
