'use strict';

const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const bodyParser = require('body-parser');
const routes = require('./routes'); // Assuming you have a routes file

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Middleware configuration
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Serve static files if needed
// app.use(express.static('public')); // Uncomment to serve static files

// WebSocket connection setup
wss.on('connection', (ws) => {
    console.log('New client connected');
    ws.on('message', (message) => {
        console.log(`Received message: ${message}`);
        // Handle incoming messages
    });
    ws.on('close', () => {
        console.log('Client disconnected');
    });
});

// Routing configuration
app.use('/api', routes);

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server is listening on port ${PORT}`);
});
