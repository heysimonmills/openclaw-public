#!/usr/bin/env node
/**
 * Verify status properties in migrated databases
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

async function main() {
    console.log('=== Checking Status Properties ===\n');
    
    const databases = [
        { id: '30a44b5e-ebe5-810e-8a22-d517de793bc6', name: 'GJC Projects' },
        { id: '30a44b5e-ebe5-8188-ab14-c5d0f19b3cb2', name: 'GJC Editing Tracker' },
        { id: '30a44b5e-ebe5-810a-8467-c8840ae1c145', name: 'GJC Tasks Archive' }
    ];
    
    for (const db of databases) {
        try {
            const database = await notionRequest(`/databases/${db.id}`, GSG_TOKEN);
            console.log(`\n📊 ${db.name}:`);
            
            // Find status property
            const statusProp = Object.entries(database.properties).find(([key, prop]) => 
                prop.type === 'status' || prop.type === 'select'
            );
            
            if (statusProp) {
                const [name, prop] = statusProp;
                console.log(`   Property "${name}" type: ${prop.type}`);
                
                if (prop.type === 'select' && prop.select?.options) {
                    console.log(`   Options: ${prop.select.options.map(o => o.name).join(', ')}`);
                } else if (prop.type === 'status' && prop.status?.options) {
                    console.log(`   Options: ${prop.status.options.map(o => o.name).join(', ')}`);
                }
            } else {
                console.log('   No status/select property found');
            }
            
            // Sample entry to verify data
            const entries = await notionRequest(`/databases/${db.id}/query`, GSG_TOKEN, {
                method: 'POST',
                body: { page_size: 1 }
            });
            
            if (entries.results.length > 0) {
                const entry = entries.results[0];
                const titleProp = Object.values(entry.properties).find(p => p.type === 'title');
                const title = titleProp?.title?.[0]?.plain_text || 'Untitled';
                
                const statusValue = Object.values(entry.properties).find(p => 
                    p.type === 'select' || p.type === 'status'
                );
                const status = statusValue?.select?.name || statusValue?.status?.name || 'None';
                
                console.log(`   Sample entry: "${title}" - Status: ${status}`);
            }
            
        } catch (e) {
            console.log(`\n❌ ${db.name}: ${e.message}`);
        }
    }
}

main().catch(console.error);
