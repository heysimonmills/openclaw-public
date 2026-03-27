#!/usr/bin/env node
/**
 * Find where existing GJ Content Plan is located
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
    console.log('=== Finding GJ Content Plan Location ===\n');
    
    // Get the GJ Content Plan database
    const gjContentPlanId = '2fa44b5e-ebe5-8115-8a44-c742824528cf';
    
    const db = await notionRequest(`/databases/${gjContentPlanId}`, GSG_TOKEN);
    console.log('Database:', db.title?.[0]?.plain_text || 'Untitled');
    console.log('Parent type:', db.parent?.type);
    console.log('Parent ID:', db.parent?.page_id || db.parent?.workspace || 'N/A');
    
    if (db.parent?.page_id) {
        // Get the parent page
        try {
            const parent = await notionRequest(`/pages/${db.parent.page_id}`, GSG_TOKEN);
            const parentTitle = parent.properties?.title?.title?.[0]?.plain_text 
                || 'Untitled';
            console.log('\nParent page:', parentTitle);
            console.log('Parent URL:', parent.url);
            
            // Get parent's parent
            if (parent.parent?.page_id) {
                const grandparent = await notionRequest(`/pages/${parent.parent.page_id}`, GSG_TOKEN);
                const grandparentTitle = grandparent.properties?.title?.title?.[0]?.plain_text 
                    || 'Untitled';
                console.log('\nGrandparent page:', grandparentTitle);
                console.log('Grandparent URL:', grandparent.url);
            }
        } catch (e) {
            console.log('Could not fetch parent:', e.message);
        }
    }
    
    // Also check the Daily To Dos database location
    console.log('\n\n--- Daily To Dos Location ---');
    const dailyTodosId = '2f644b5e-ebe5-8079-9d9a-cf3f9b6aa62d';
    const dailyDb = await notionRequest(`/databases/${dailyTodosId}`, GSG_TOKEN);
    console.log('Parent type:', dailyDb.parent?.type);
    console.log('Parent ID:', dailyDb.parent?.page_id || 'N/A');
    
    if (dailyDb.parent?.page_id) {
        try {
            const parent = await notionRequest(`/pages/${dailyDb.parent.page_id}`, GSG_TOKEN);
            console.log('Parent:', parent.properties?.title?.title?.[0]?.plain_text || 'Untitled');
        } catch (e) {
            console.log('Could not fetch parent');
        }
    }
}

main().catch(console.error);
