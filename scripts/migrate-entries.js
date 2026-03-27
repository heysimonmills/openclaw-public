#!/usr/bin/env node
/**
 * Migrate entries from GJC Projects, Editing Tracker, and Tasks databases
 * Now that status properties have been fixed to select type
 */

const GJC_TOKEN = 'YOUR_NOTION_API_TOKEN';
const GSG_TOKEN = 'YOUR_NOTION_API_TOKEN';

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

async function getAllEntries(dbId, token) {
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
    
    return entries;
}

function transformValue(prop, value) {
    if (!value) return null;
    
    switch (prop.type) {
        case 'title':
            return {
                title: value.title?.map(t => ({
                    type: 'text',
                    text: { content: t.plain_text || t.text?.content || '' }
                })) || []
            };
            
        case 'rich_text':
            return {
                rich_text: value.rich_text?.map(t => ({
                    type: 'text',
                    text: { content: t.plain_text || t.text?.content || '' }
                })) || []
            };
            
        case 'number':
            return value.number !== null ? { number: value.number } : null;
            
        case 'select':
            return value.select ? { select: { name: value.select.name } } : null;
            
        case 'multi_select':
            return {
                multi_select: value.multi_select?.map(s => ({ name: s.name })) || []
            };
            
        case 'date':
            return value.date ? {
                date: {
                    start: value.date.start,
                    end: value.date.end || undefined
                }
            } : null;
            
        case 'checkbox':
            return { checkbox: value.checkbox || false };
            
        case 'url':
            return value.url ? { url: value.url } : null;
            
        case 'email':
            return value.email ? { email: value.email } : null;
            
        case 'phone_number':
            return value.phone_number ? { phone_number: value.phone_number } : null;
            
        case 'status':
            return value.status ? { select: { name: value.status.name } } : null;
            
        case 'people':
        case 'relation':
        case 'rollup':
        case 'formula':
        case 'created_time':
        case 'created_by':
        case 'last_edited_time':
        case 'last_edited_by':
            return null; // Skip these
            
        case 'files':
            if (value.files && value.files.length > 0) {
                return {
                    files: value.files.map(f => ({
                        name: f.name,
                        external: f.external ? { url: f.external.url } : undefined,
                        file: f.file ? { url: f.file.url, expiry_time: f.file.expiry_time } : undefined
                    })).filter(f => f.external || f.file)
                };
            }
            return null;
            
        default:
            return null;
    }
}

function transformBlocks(blocks) {
    if (!blocks || blocks.length === 0) return [];
    
    return blocks.map(block => {
        const type = block.type;
        
        try {
            switch (type) {
                case 'paragraph':
                    return {
                        object: 'block',
                        type: 'paragraph',
                        paragraph: {
                            rich_text: block.paragraph?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || []
                        }
                    };
                case 'heading_1':
                    return {
                        object: 'block',
                        type: 'heading_1',
                        heading_1: {
                            rich_text: block.heading_1?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || []
                        }
                    };
                case 'heading_2':
                    return {
                        object: 'block',
                        type: 'heading_2',
                        heading_2: {
                            rich_text: block.heading_2?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || []
                        }
                    };
                case 'heading_3':
                    return {
                        object: 'block',
                        type: 'heading_3',
                        heading_3: {
                            rich_text: block.heading_3?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || []
                        }
                    };
                case 'bulleted_list_item':
                    return {
                        object: 'block',
                        type: 'bulleted_list_item',
                        bulleted_list_item: {
                            rich_text: block.bulleted_list_item?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || []
                        }
                    };
                case 'numbered_list_item':
                    return {
                        object: 'block',
                        type: 'numbered_list_item',
                        numbered_list_item: {
                            rich_text: block.numbered_list_item?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || []
                        }
                    };
                case 'to_do':
                    return {
                        object: 'block',
                        type: 'to_do',
                        to_do: {
                            rich_text: block.to_do?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || [],
                            checked: block.to_do?.checked || false
                        }
                    };
                case 'quote':
                    return {
                        object: 'block',
                        type: 'quote',
                        quote: {
                            rich_text: block.quote?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || []
                        }
                    };
                case 'callout':
                    return {
                        object: 'block',
                        type: 'callout',
                        callout: {
                            rich_text: block.callout?.rich_text?.map(t => ({
                                type: 'text',
                                text: { content: t.plain_text || t.text?.content || '' }
                            })) || [],
                            icon: block.callout?.icon || { emoji: '💡' }
                        }
                    };
                case 'divider':
                    return { object: 'block', type: 'divider', divider: {} };
                default:
                    return null;
            }
        } catch (e) {
            return null;
        }
    }).filter(b => b !== null);
}

async function migrateEntries(dbKey) {
    const { source, target, titleProp } = DATABASES[dbKey];
    console.log(`\n📦 Migrating ${dbKey}...`);
    
    // Get source database schema
    const sourceDb = await notionRequest(`/databases/${source}`, GJC_TOKEN);
    
    // Get all entries
    const entries = await getAllEntries(source, GJC_TOKEN);
    console.log(`  Found ${entries.length} entries`);
    
    let success = 0;
    let errors = 0;
    
    for (let i = 0; i < entries.length; i++) {
        const entry = entries[i];
        
        try {
            // Transform properties
            const properties = {};
            for (const [key, prop] of Object.entries(sourceDb.properties)) {
                const value = entry.properties[key];
                const transformed = transformValue(prop, value);
                if (transformed) {
                    properties[key] = transformed;
                }
            }
            
            // Get page content
            let children = [];
            try {
                const content = await notionRequest(`/blocks/${entry.id}/children`, GJC_TOKEN);
                children = transformBlocks(content.results || []);
            } catch (e) {
                // Some entries might not have content
            }
            
            // Create in target
            await notionRequest('/pages', GSG_TOKEN, {
                method: 'POST',
                body: {
                    parent: { database_id: target },
                    properties,
                    children
                }
            });
            
            success++;
            process.stdout.write(`\r  Progress: ${i + 1}/${entries.length} (${success}✓ ${errors}✗)`);
            
            // Rate limiting - small delay
            await new Promise(r => setTimeout(r, 350));
            
        } catch (error) {
            errors++;
            process.stdout.write(`\r  Progress: ${i + 1}/${entries.length} (${success}✓ ${errors}✗)`);
        }
    }
    
    console.log(`\n  ✅ Migrated ${success} entries (${errors} errors)`);
    return { success, errors };
}

async function main() {
    console.log('=== Migrating GJC Database Entries ===\n');
    
    const results = {};
    
    try {
        for (const dbKey of Object.keys(DATABASES)) {
            results[dbKey] = await migrateEntries(dbKey);
        }
        
        console.log('\n' + '='.repeat(50));
        console.log('📋 SUMMARY');
        console.log('='.repeat(50));
        
        let totalSuccess = 0;
        let totalErrors = 0;
        
        for (const [dbKey, result] of Object.entries(results)) {
            console.log(`${dbKey}: ${result.success} success, ${result.errors} errors`);
            totalSuccess += result.success;
            totalErrors += result.errors;
        }
        
        console.log(`\nTotal: ${totalSuccess} entries migrated, ${totalErrors} errors`);
        console.log('\n✨ Migration complete!');
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}

main();
