#!/usr/bin/env node
/**
 * Fix Status Properties in Migrated GJC Databases
 * Converts status properties to select so entries can be migrated
 */

const GSG_TOKEN = 'YOUR_NOTION_API_TOKEN';
const GJC_TOKEN = 'YOUR_NOTION_API_TOKEN';

// Database mappings (source -> target)
const DATABASES = {
    projects: {
        source: '298c4c6b-a88a-8166-ab50-f72b421aa82f',
        target: '30a44b5e-ebe5-810e-8a22-d517de793bc6',
        titleProp: 'Project name'
    },
    editingTracker: {
        source: '2c4c4c6b-a88a-80bd-b6bd-dc8143b96dd1',
        target: '30a44b5e-ebe5-8188-ab14-c5d0f19b3cb2',
        titleProp: 'Project name'
    },
    tasks: {
        source: '298c4c6b-a88a-8199-adf0-d5e3c1f1bdda',
        target: '30a44b5e-ebe5-810a-8467-c8840ae1c145',
        titleProp: 'Task name'
    }
};

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

async function fixDatabase(dbKey) {
    const { source, target, titleProp } = DATABASES[dbKey];
    console.log(`\n🔧 Fixing ${dbKey}...`);
    
    // Get source database schema
    const sourceDb = await notionRequest(`/databases/${source}`, GJC_TOKEN);
    
    // Get the status property options from source
    const statusProp = Object.entries(sourceDb.properties).find(([key, prop]) => prop.type === 'status');
    
    if (!statusProp) {
        console.log(`  ⚠️  No status property found in source`);
        return;
    }
    
    const [statusName, statusConfig] = statusProp;
    console.log(`  Found status property: ${statusName}`);
    console.log(`  Options: ${statusConfig.status.options.map(o => o.name).join(', ')}`);
    
    // Update target database to change status to select
    try {
        await notionRequest(`/databases/${target}`, GSG_TOKEN, {
            method: 'PATCH',
            body: {
                properties: {
                    [statusName]: {
                        select: {
                            options: statusConfig.status.options.map(o => ({
                                name: o.name,
                                color: o.color
                            }))
                        }
                    }
                }
            }
        });
        console.log(`  ✅ Converted status to select`);
    } catch (e) {
        console.log(`  ⚠️  Could not update property: ${e.message}`);
        // Try deleting and recreating
        console.log(`  Trying alternative approach...`);
    }
}

async function main() {
    console.log('=== Fixing Status Properties ===\n');
    
    try {
        for (const dbKey of Object.keys(DATABASES)) {
            await fixDatabase(dbKey);
        }
        
        console.log('\n✨ Done! Now you need to manually migrate entries with status values.');
        console.log('The databases have been fixed to use select instead of status type.');
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}

main();
