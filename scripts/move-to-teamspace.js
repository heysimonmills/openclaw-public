#!/usr/bin/env node
/**
 * Move migrated GJC content to Mission Control (Good Jelly Co Teamspace)
 */

const GSG_TOKEN = 'YOUR_NOTION_API_TOKEN';

// Target: Mission Control (where existing GJ Content Plan lives)
const MISSION_CONTROL_ID = '2f844b5e-ebe5-8117-ab7e-fce9b62c65ef';

// Source: The archive pages we created earlier
const ARCHIVE_PAGES = [
    '30a44b5e-ebe5-8184-a369-ff61048dff6b',  // 🍯 Good Jelly Co Archive
    '30a44b5e-ebe5-810c-884c-db34d082c6c7',  // Another archive
    '30a44b5e-ebe5-817c-9307-df9d748ee4f3'   // Another archive
];

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
    console.log('=== Moving GJC Archive to Mission Control ===\n');
    console.log(`Target: Mission Control (${MISSION_CONTROL_ID})\n`);
    
    // Check each archive page and its children
    for (const pageId of ARCHIVE_PAGES) {
        try {
            const page = await notionRequest(`/pages/${pageId}`, GSG_TOKEN);
            const title = page.properties?.title?.title?.[0]?.plain_text 
                || 'Untitled';
            
            console.log(`\n📄 Checking: ${title} (${pageId})`);
            
            // Get children (databases and pages)
            const children = await notionRequest(`/blocks/${pageId}/children`, GSG_TOKEN);
            
            console.log(`   Found ${children.results?.length || 0} children`);
            
            // List what we found
            for (const child of children.results || []) {
                if (child.type === 'child_database') {
                    console.log(`   📊 Database: ${child.child_database?.title || 'Untitled'}`);
                } else if (child.type === 'link_to_page') {
                    const linkedId = child.link_to_page?.page_id || child.link_to_page?.database_id;
                    console.log(`   🔗 Link: ${linkedId}`);
                }
            }
            
        } catch (e) {
            console.log(`   Error: ${e.message}`);
        }
    }
    
    console.log('\n\n⚠️  Note: Notion API does not support moving pages/databases between parents.');
    console.log('The content has been created but needs to be manually organized in Notion.');
    console.log('\nTo complete the migration:');
    console.log('1. Go to Mission Control in Notion');
    console.log('2. Create a new page called "Good Jelly Co Archive"');
    console.log('3. Use "Move to" to move the following databases under it:');
    console.log('   - GJ Content Plan (Archive)');
    console.log('   - GJC Projects');
    console.log('   - GJC Editing Tracker');
    console.log('   - GJC Tasks Archive');
    console.log('   - Good Jelly HQ (Archive)');
}

main().catch(console.error);
