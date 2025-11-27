const express = require('express');
const enforcePolicy = require('./enforcePolicyMiddleware');

const app = express();
const port = 3000;

// Middleware to parse JSON bodies
app.use(express.json());

// A protected route that uses the OPA policy enforcement middleware
app.post('/register', enforcePolicy, (req, res) => {
  // This code will only execute if the policy allows the request
  res.status(200).send({
    allowed: true,
    message: 'Template registration successful'
  });
});

app.listen(port, () => {
  console.log(`API server listening at http://localhost:${port}`);
});
