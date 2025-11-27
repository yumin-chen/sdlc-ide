const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');

const app = express();
const PORT = 3000;
const OPA_URL = 'http://localhost:8181/v1/data/sdlc/governance/allow';

app.use(bodyParser.json());

/**
 * Orchestrator Governance Agent - Webhook Handler
 * Receives events from Git Server (e.g., GitHub)
 */
app.post('/webhook', async (req, res) => {
    const event = req.headers['x-github-event'];
    const payload = req.body;

    console.log(`Received event: ${event}`);

    // 1. Construct OPA Input
    const input = buildOpaInput(event, payload);

    try {
        // 2. Query OPA
        const opaResponse = await axios.post(OPA_URL, { input });
        const allowed = opaResponse.data.result;

        // 3. Enforce Decision
        if (allowed) {
            console.log('✅ Action Allowed by Policy');
            // Trigger downstream orchestration (e.g., update search index, notify agents)
            triggerOrchestration(payload);
            res.status(200).send('Allowed');
        } else {
            console.error('❌ Action Blocked by Policy');
            // Take remediation action (e.g., revert commit, post comment on PR)
            await handleViolation(payload);
            res.status(403).send('Blocked by Policy');
        }
    } catch (error) {
        console.error('Error querying OPA:', error.message);
        res.status(500).send('Internal Server Error');
    }
});

function buildOpaInput(event, payload) {
    // Map GitHub payload to OPA input schema
    return {
        event_type: event === 'push' ? 'push' : 'pull_request',
        action: payload.action || 'updated',
        pull_request: payload.pull_request ? {
            merged: payload.pull_request.merged,
            merged_by: payload.pull_request.merged_by,
            approvals: 0 // In real app, fetch reviews API
        } : null,
        changed_files: [], // In real app, fetch commit diff
        actor: payload.sender.login,
        repo: payload.repository.full_name
    };
}

function triggerOrchestration(payload) {
    console.log('-> Triggering TSD Manager...');
    console.log('-> Triggering Embedding Service...');
}

async function handleViolation(payload) {
    console.log('-> Posting violation comment to PR...');
    console.log('-> Logging audit event...');
}

app.listen(PORT, () => {
    console.log(`Governance Agent listening on port ${PORT}`);
});
