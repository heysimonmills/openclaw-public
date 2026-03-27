#!/usr/bin/env node
/**
 * Create comprehensive migration report
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
    console.log('# Good Jelly Co to GSG Migration Report\n');
    console.log('**Date:** 2026-02-17\n');
    
    // Source databases
    console.log('## Source (Good Jelly Co Workspace)\n');
    const gjcDbs = [
        { id: '2a3c4c6b-a88a-8062-a413-e6ea537542d7', name: 'GJ Content Plan' },
        { id: '298c4c6b-a88a-8166-ab50-f72b421aa82f', name: 'Projects' },
        { id: '2c4c4c6b-a88a-80bd-b6bd-dc8143b96dd1', name: 'Editing Tracker' },
        { id: '298c4c6b-a88a-8199-adf0-d5e3c1f1bdda', name: 'Tasks' }
    ];
    
    for (const db of gjcDbs) {
        try {
            const count = await countEntries(db.id, GJC_TOKEN);
            console.log(`- **${db.name}**: ${count} entries`);
        } catch (e) {
            console.log(`- **${db.name}**: Error counting - ${e.message}`);
        }
    }
    
    // Target databases
    console.log('\n## Target (GSG Workspace - Migrated)\n');
    
    const migratedDbs = [
        { 
            id: '30a44b5e-ebe5-81be-b88b-cf264db73ba2', 
            name: 'GJ Content Plan (Archive)',
            source: '2a3c4c6b-a88a-8062-a413-e6ea537542d7'
        },
        { 
            id: '30a44b5e-ebe5-810e-8a22-d517de793bc6', 
            name: 'GJC Projects',
            source: '298c4c6b-a88a-8166-ab50-f72b421aa82f'
        },
        { 
            id: '30a44b5e-ebe5-8188-ab14-c5d0f19b3cb2', 
            name: 'GJC Editing Tracker',
            source: '2c4c4c6b-a88a-80bd-b6bd-dc8143b96dd1'
        },
        { 
            id: '30a44b5e-ebe5-810a-8467-c8840ae1c145', 
            name: 'GJC Tasks Archive',
            source: '298c4c6b-a88a-8199-adf0-d5e3c1f1bdda'
        }
    ];
    
    let totalMigrated = 0;
    
    for (const db of migratedDbs) {
        try {
            const count = await countEntries(db.id, GSG_TOKEN);
            totalMigrated += count;
            const url = `https://notion.so/${db.id.replace(/-/g, '')}`;
            console.log(`- **${db.name}**: ${count} entries`);
            console.log(`  - URL: ${url}`);
        } catch (e) {
            console.log(`- **${db.name}**: Error counting - ${e.message}`);
        }
    }
    
    // Existing GSG databases
    console.log('\n## Existing GSG Databases (Good Jelly Co Teamspace)\n');
    console.log('- **GJ Content Plan** (existing): `2fa44b5e-ebe5-8115-8a44-c742824528cf`');
    console.log('  - Already exists in Mission Control (Good Jelly Co Teamspace)');
    console.log('  - Schema compared with GJC version - some properties differ');
    console.log('- **Daily To Dos** (existing): `2f644b5e-ebe5-8079-9d9a-cf3f9b6aa62d`');
    console.log('  - Already exists in Mission Control');
    
    // Archive pages
    console.log('\n## Archive Pages Created\n');
    console.log('- **🍯 Good Jelly Co Archive** (main container)');
    console.log('  - ID: `30a44b5e-ebe5-8184-a369-ff61048dff6b`');
    console.log('  - URL: https://notion.so/30a44b5eebe58184a369ff61048dff6b');
    console.log('- **Good Jelly HQ (Archive)**');
    console.log('  - ID: `30a44b5e-ebe5-81bb-97a1-f3c76eb8576c`');
    
    // Summary
    console.log('\n## Summary\n');
    console.log(`- **Total entries migrated**: ${totalMigrated}`);
    console.log('- **Databases created**: 4');
    console.log('- **Pages created**: 2');
    console.log('- **Location**: Currently in "🍯 Good Jelly Co Archive" page');
    console.log('- **Target location**: Mission Control (Good Jelly Co Teamspace)');
    
    console.log('\n## Issues & Notes\n');
    console.log('1. **Status Properties**: Databases with "status" type properties were converted to "select" type');
    console.log('   - This allows entries to be migrated successfully');
    console.log('   - Status values are preserved but displayed as select dropdowns');
    console.log('2. **Relations**: Relation properties were skipped (cannot be auto-created)');
    console.log('   - Must be manually recreated in Notion if needed');
    console.log('3. **Location**: Content is NOT in Mission Control yet');
    console.log('   - Notion API does not support moving pages between parents');
    console.log('   - Must use Notion UI to move content (see next steps)');
    
    console.log('\n## Next Steps\n');
    console.log('### Option 1: Move Content in Notion UI (Recommended)');
    console.log('1. Open GSG workspace in Notion');
    console.log('2. Navigate to "🍯 Good Jelly Co Archive" page');
    console.log('3. Select all databases and pages');
    console.log('4. Use "Move to" → "Mission Control" to move them to the Good Jelly Co Teamspace');
    console.log('');
    console.log('### Option 2: Create New Archive in Mission Control');
    console.log('1. Go to Mission Control in Notion');
    console.log('2. Create a new page called "Good Jelly Co Archive (Migrated)"');
    console.log('3. Copy/move the migrated databases to this new page');
    console.log('');
    console.log('### Option 3: Merge with Existing');
    console.log('1. Keep GJ Content Plan (Archive) as historical record');
    console.log('2. Manually copy any new content to the existing GJ Content Plan in Mission Control');
    console.log('3. Use GJC Projects, Editing Tracker, and Tasks Archive as separate reference databases');
}

main().catch(console.error);
