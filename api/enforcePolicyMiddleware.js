const fetch = require('node-fetch');

const enforcePolicy = async (req, res, next) => {
    const opaUrl = process.env.OPA_URL;
    if (!opaUrl) {
        return res.status(500).send({ error: 'OPA_URL environment variable not set' });
    }

    try {
        // For this prototype, the action is hardcoded.
        // The actor and template are expected in the request body.
        const input = {
            action: "register_template",
            actor: req.body.actor,
            template: req.body.template
        };

        const response = await fetch(opaUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input })
        });

        const decision = await response.json();

        if (decision.result && decision.result.allow) {
            // Policy allows the action, proceed to the next middleware/handler.
            next();
        } else {
            // Policy denies the action.
            const reasons = decision.result && decision.result.reasons ? decision.result.reasons : ['Policy denied'];
            return res.status(403).send({
                allowed: false,
                reasons: reasons
            });
        }
    } catch (error) {
        console.error('Error contacting OPA:', error);
        return res.status(500).send({ error: 'Failed to evaluate policy with OPA' });
    }
};

module.exports = enforcePolicy;
