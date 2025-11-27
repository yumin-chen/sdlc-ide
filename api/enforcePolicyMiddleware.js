const fetch = require('node-fetch');

const enforcePolicy = async (req, res, next) => {
  const opaUrl = process.env.OPA_URL;

  if (!opaUrl) {
    console.error('OPA_URL environment variable not set.');
    return res.status(500).json({ success: false, message: 'Policy service is not configured.' });
  }

  // Assume the request body contains the necessary structure for the policy input
  const { actor, template } = req.body;
  const action = req.path === '/register' ? 'register_template' : 'unknown'; // Simple action mapping

  if (!actor || !template) {
      return res.status(400).json({ success: false, message: 'Invalid request body: "actor" and "template" fields are required.' });
  }

  const input = {
    action,
    actor,
    template,
  };

  try {
    const response = await fetch(opaUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input }),
    });

    if (!response.ok) {
        const errorText = await response.text();
        console.error(`OPA service returned an error: ${response.status}`, errorText);
        return res.status(500).json({ success: false, message: 'Failed to evaluate policy.' });
    }

    const policyResult = await response.json();

    // OPA response for a single rule is typically {"result": ...}
    const decision = policyResult.result;

    if (decision && decision.allow) {
      next(); // Policy allows the request
    } else {
      // Policy denies the request, include reasons if available
      const reasons = decision ? decision.reasons : ['No specific reason provided.'];
      res.status(403).json({
          success: false,
          message: 'Request denied by policy.',
          reasons: reasons
      });
    }
  } catch (error) {
    console.error('Error connecting to OPA service:', error);
    res.status(500).json({ success: false, message: 'Could not connect to policy service.' });
  }
};

module.exports = enforcePolicy;
