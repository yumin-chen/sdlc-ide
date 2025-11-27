const express = require('express');
const enforcePolicy = require('./enforcePolicyMiddleware');

const app = express();
const port = 3000;

app.use(express.json());

app.get('/', (req, res) => {
  res.send('API Server is running!');
});

app.post('/register', enforcePolicy, (req, res) => {
  res.status(200).json({ success: true, message: 'Template registration is allowed.' });
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
