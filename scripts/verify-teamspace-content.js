#!/usr/bin/env node
/**
 * Verify migrated content in Good Jelly Co Teamspace
 */

const GSG_TOKEN = 'YOUR_NOTION_API_TOKEN';

async function notionRequest(endpoint, token, options = {}) {
    const url = `https://api.notion.com/v1${endpoint}`;
    const response = await fetch(url, {
        method: options.method || 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json',
            ...options.headers
        },
        body: options.body ? JSON.stringify(options.body) : undefined
    });
    
    if (!response.ok) {
        const error = await response.text();
        throw new Error(`Notion API error: ${response.status} - ${error}`);
    }
    
    return response.json();
}

async function countEntries(dbId, token) {
    const entries = [];
    let cursor = undefined;
    
    do {
        const body = { page_size: 100 };
        if (cursor) body.start_cursor = cursor;
        
        const response = await notionRequest(`/databases/${dbId}/query`, token, {
            method: 'POST',
            body
        });
        
        entries.push(...response.results);
        cursor = response.next_cursor;
        
    } while (cursor);
    
    return entries.length;
}

async function main() {
    console.log('=== Migrated Content in Good Jelly Co Teamspace ===\n');
    console.log('Teamspace Root: Teamspace Home (30a44b5e-ebe5-810b-a017-eedc32b9ec1a)\n');
    
    const databases = [
        { id: '30a44b5e-ebe5-81be-b88b-cf264db73ba2', name: 'GJ Content Plan (Archive)' },
        { id: '30a44b5e-ebe5-810e-8a22-d517de793bc6', name: 'GJC Projects' },
        { id: '30a44b5e-ebe5-8188-ab14-c5d0f19b3cb2', name: 'GJC Editing Tracker' },
        { id: '30a44b5e-ebe5-810a-8467-c8840ae1c145', name: 'GJC Tasks Archive' },
        { id: '30a44b5e-ebe5-815d-85f0-fb924aa637a4', name: 'GJ Content Plan (Archive) - Extra' }
    ];
    
    let total = 0;
    
    for (const db of databases) {
        try {
            const count = await countEntries(db.id, GSG_TOKEN);
            total += count;
            const url = `https://notion.so/${db.id.replace(/-/g, '')}`;
            console.log(`✅ ${db.name}: ${count} entries`);
            console.log(`   ${url}\n`);
        } catch (e) {
            console.log(`❌ ${db.name}: Error - ${e.message}\n`);
        }
    }
    
    console.log('='.repeat(50));
    console.log(`Total entries migrated: ${total}`);
    console.log('='.repeat(50));
}

main().catch(console.error);
