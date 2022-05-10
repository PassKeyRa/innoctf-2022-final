const express = require('express')
const fs = require('fs');
const app = express()

var CONTRACT_ADDRESS = fs.readFileSync('address', 'utf8');

var PORT = process.env.PORT || 8001
var BIND_ADDR = process.env.BIND_ADDR || '0.0.0.0'

app.get('/contract', function(req, res){
  res.send(CONTRACT_ADDRESS)
})

app.listen(PORT, BIND_ADDR, () => {
  console.log('Contract info is running on ' + BIND_ADDR + ':' + PORT)
})
