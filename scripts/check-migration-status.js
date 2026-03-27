#!/usr/bin/env node
/**
 * Check current migration status
 */

const GJC_TOKEN = 'YOUR_NOTION_API_TOKEN';
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
    try {
        const response = await notionRequest(`/databases/${dbId}/query`, token, {
            method: 'POST',
            body: { page_size: 1 }
        });
        
        // Get total by iterating (Notion doesn't give total count directly)
        let count = 0;
        let cursor = undefined;
        
        do {
            const body = { page_size: 100 };
            if (cursor) body.start_cursor = cursor;
            
            const resp = await notionRequest(`/databases/${dbId}/query`, token, {
                method: 'POST',
                body
            });
            
            count += resp.results.length;
            cursor = resp.next_cursor;
            
        } while (cursor);
        
        return count;
    } catch (e) {
        return `Error: ${e.message}`;
    }
}

async function main() {
    console.log('=== MIGRATION STATUS CHECK ===\n');
    
    // Check GJC workspace
    console.log('📊 GOOD JELLY CO WORKSPACE (Source)');
    console.log('=' .repeat(50));
    
    const gjcDbs = [
        { id: '2a3c4c6b-a88a-8062-a413-e6ea537542d7', name: 'GJ Content Plan' },
        { id: '298c4c6b-a88a-8166-ab50-f72b421aa82f', name: 'Projects' },
        { id: '2c4c4c6b-a88a-80bd-b6bd-dc8143b96dd1', name: 'Editing Tracker' },
        { id: '298c4c6b-a88a-8199-adf0-d5e3c1f1bdda', name: 'Tasks' }
    ];
    
    for (const db of gjcDbs) {
        const count = await countEntries(db.id, GJC_TOKEN);
        console.log(`${db.name}: ${count} entries`);
    }
    
    // Check GSG workspace for migrated content
    console.log('\n\n📊 GSG WORKSPACE (Target - Migrated Content)');
    console.log('=' .repeat(50));
    
    const gsgDbs = [
        { id: '30a44b5e-ebe5-81be-b88b-cf264db73ba2', name: 'GJ Content Plan (Archive)' },
        { id: '30a44b5e-ebe5-810e-8a22-d517de793bc6', name: 'GJC Projects' },
        { id: '30a44b5e-ebe5-8188-ab14-c5d0f19b3cb2', name: 'GJC Editing Tracker' },
        { id: '30a44b5e-ebe5-810a-8467-c8840ae1c145', name: 'GJC Tasks Archive' }
    ];
    
    let totalMigrated = 0;
    
    for (const db of gsgDbs) {
        const count = await countEntries(db.id, GSG_TOKEN);
        if (typeof count === 'number') totalMigrated += count;
        console.log(`${db.name}: ${count} entries`);
    }
    
    // Check for the archive page
    console.log('\n\n📄 ARCHIVE PAGE IN GSG');
    console.log('=' .repeat(50));
    
    try {
        const archivePage = await notionRequest('/pages/30a44b5e-ebe5-8184-a369-ff61048dff6b', GSG_TOKEN);
        const title = archivePage.properties?.title?.title?.[0]?.plain_text || 'Untitled';
        console.log(`✅ Archive page exists: "${title}"`);
        console.log(`   Location: Good Jelly Co Teamspace (Teamspace Home)`);
        console.log(`   URL: https://notion.so/30a44b5eebe58184a369ff61048dff6b`);
    } catch (e) {
        console.log(`❌ Archive page not found: ${e.message}`);
    }
    
    console.log('\n\n' + '='.repeat(50));
    console.log('SUMMARY');
    console.log('='.repeat(50));
    console.log(`Total entries in GSG: ${totalMigrated}`);
    console.log(`Migration status: ${totalMigrated > 0 ? '✅ COMPLETE' : '❌ NOT STARTED'}`);
}

main().catch(console.error);
