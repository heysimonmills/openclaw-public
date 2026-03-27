#!/usr/bin/env node
/**
 * Check Teamspace Home contents
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
    console.log('=== Teamspace Home Contents ===\n');
    
    const teamspaceId = '30a44b5e-ebe5-810b-a017-eedc32b9ec1a';
    
    // Get the page details
    const page = await notionRequest(`/pages/${teamspaceId}`, GSG_TOKEN);
    const title = page.properties?.title?.title?.[0]?.plain_text || 'Untitled';
    console.log(`Page: ${title}`);
    console.log(`ID: ${teamspaceId}`);
    console.log(`URL: ${page.url}\n`);
    
    // Get child blocks
    const children = await notionRequest(`/blocks/${teamspaceId}/children`, GSG_TOKEN);
    
    console.log(`Found ${children.results?.length || 0} children:\n`);
    
    for (const child of children.results || []) {
        if (child.type === 'child_database') {
            console.log(`📊 Database: ${child.child_database?.title || 'Untitled'}`);
            console.log(`   ID: ${child.id}`);
        } else if (child.type === 'child_page') {
            console.log(`📄 Page: ${child.child_page?.title || 'Untitled'}`);
            console.log(`   ID: ${child.id}`);
        } else if (child.type === 'link_to_page') {
            const linkedId = child.link_to_page?.page_id || child.link_to_page?.database_id;
            console.log(`🔗 Link: ${linkedId}`);
        } else if (child.type === 'paragraph') {
            const text = child.paragraph?.rich_text?.map(t => t.plain_text).join('') || '';
            if (text.trim()) {
                console.log(`📝 Text: ${text.substring(0, 80)}${text.length > 80 ? '...' : ''}`);
            }
        } else {
            console.log(`⬜ ${child.type}`);
        }
    }
    
    // Also check if there's a Mission Control link or reference
    console.log('\n=== Searching for Mission Control ===\n');
    
    const missionControlId = '2f844b5e-ebe5-8117-ab7e-fce9b62c65ef';
    try {
        const mc = await notionRequest(`/pages/${missionControlId}`, GSG_TOKEN);
        const mcTitle = mc.properties?.title?.title?.[0]?.plain_text || 'Untitled';
        console.log(`Found Mission Control: ${mcTitle}`);
        console.log(`Parent: ${mc.parent?.type}`);
        if (mc.parent?.page_id === teamspaceId) {
            console.log('✅ Mission Control is a child of Teamspace Home!');
        } else if (mc.parent?.workspace) {
            console.log('⚠️  Mission Control is at workspace level');
        }
    } catch (e) {
        console.log('Could not fetch Mission Control:', e.message);
    }
}

main().catch(console.error);
