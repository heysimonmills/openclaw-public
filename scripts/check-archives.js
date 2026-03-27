#!/usr/bin/env node
/**
 * Check which archive has the migrated databases
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
    console.log('=== Checking Archive Pages ===\n');
    
    const archiveIds = [
        '30a44b5e-ebe5-8184-a369-ff61048dff6b',
        '30a44b5e-ebe5-810c-884c-db34d082c6c7',
        '30a44b5e-ebe5-817c-9307-df9d748ee4f3'
    ];
    
    for (const id of archiveIds) {
        try {
            const page = await notionRequest(`/pages/${id}`, GSG_TOKEN);
            const title = page.properties?.title?.title?.[0]?.plain_text || 'Untitled';
            const parentId = page.parent?.page_id;
            
            console.log(`\n📄 ${title}`);
            console.log(`   ID: ${id}`);
            console.log(`   Parent: ${parentId === '30a44b5e-ebe5-810b-a017-eedc32b9ec1a' ? '✅ Teamspace Home' : parentId}`);
            
            // Get children
            const children = await notionRequest(`/blocks/${id}/children`, GSG_TOKEN);
            console.log(`   Children (${children.results?.length || 0}):`);
            
            for (const child of children.results || []) {
                if (child.type === 'child_database') {
                    console.log(`      📊 ${child.child_database?.title || 'Untitled'} (${child.id})`);
                } else if (child.type === 'link_to_page') {
                    const linkedId = child.link_to_page?.database_id || child.link_to_page?.page_id;
                    console.log(`      🔗 Link to: ${linkedId}`);
                } else if (child.type === 'child_page') {
                    console.log(`      📄 Page: ${child.child_page?.title || 'Untitled'}`);
                }
            }
        } catch (e) {
            console.log(`\n❌ Error checking ${id}: ${e.message}`);
        }
    }
}

main().catch(console.error);
