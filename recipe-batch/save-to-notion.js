#!/usr/bin/env node

const { Client } = require('@notionhq/client');
const fs = require('fs');
const path = require('path');

// Read Notion API key
const notionApiKey = process.env.NOTION_TOKEN || 
                     process.env.NOTION_API_KEY || 
                     fs.readFileSync(path.join(process.env.HOME, '.config/notion/api_key'), 'utf8').trim();

// Initialize Notion client
const notion = new Client({
  auth: notionApiKey
});

const DATABASE_ID = 'f44b6ca9-3236-4cef-a2f1-f8441a13fb42';

// Helper to parse recipe from transcript
function parseRecipe(transcript, url) {
  const lines = transcript.trim().split('\n');
  const text = lines.join(' ');
  
  // Extract recipe name from first sentence or URL
  const firstSentence = text.split(/[.!?]/)[0];
  let recipeName = firstSentence.substring(0, 100);
  
  // Clean up common phrases
  recipeName = recipeName
    .replace(/^(If you're looking for|Here's|Welcome to|Today|This is|Did you know)/i, '')
    .replace(/^(When you|Why eat)/i, '')
    .trim();
  
  if (recipeName.length < 10) {
    recipeName = 'Instagram Recipe';
  }
  
  // Extract ingredients (words like: chicken, rice, garlic, onion, etc.)
  const ingredientKeywords = [
    'chicken', 'turkey', 'beef', 'pork', 'salmon', 'fish',
    'rice', 'pasta', 'noodles', 'bread', 'pita',
    'garlic', 'onion', 'pepper', 'salt', 'ginger',
    'soy sauce', 'honey', 'butter', 'oil', 'olive oil',
    'cheese', 'cream', 'milk', 'yogurt',
    'tomato', 'spinach', 'lettuce', 'broccoli', 'carrot',
    'pepper flakes', 'paprika', 'cumin', 'oregano',
    'teriyaki', 'sriracha', 'ketchup', 'vinegar'
  ];
  
  const foundIngredients = new Set();
  const lowerText = text.toLowerCase();
  
  ingredientKeywords.forEach(ingredient => {
    if (lowerText.includes(ingredient)) {
      foundIngredients.add(ingredient);
    }
  });
  
  const ingredients = Array.from(foundIngredients).join(', ') || 'See transcript for details';
  
  // Instructions are basically the full transcript
  const instructions = text;
  
  // Detect tags
  const tags = [];
  if (lowerText.includes('chicken')) tags.push('Chicken');
  if (lowerText.includes('beef')) tags.push('Beef');
  if (lowerText.includes('turkey')) tags.push('Turkey');
  if (lowerText.includes('salmon') || lowerText.includes('fish')) tags.push('Seafood');
  if (lowerText.includes('vegetarian') || lowerText.includes('veggie')) tags.push('Vegetarian');
  if (lowerText.includes('meal prep')) tags.push('Meal Prep');
  if (lowerText.includes('quick') || lowerText.includes('20 minutes') || lowerText.includes('30 minutes')) tags.push('Quick');
  if (lowerText.includes('korean') || lowerText.includes('asian') || lowerText.includes('teriyaki') || lowerText.includes('soy sauce')) tags.push('Asian');
  if (lowerText.includes('italian') || lowerText.includes('pasta') || lowerText.includes('alfredo')) tags.push('Italian');
  
  return {
    name: recipeName,
    url: url,
    ingredients: ingredients,
    instructions: instructions,
    tags: tags
  };
}

// Save recipe to Notion
async function saveRecipeToNotion(recipe) {
  try {
    const response = await notion.pages.create({
      parent: { database_id: DATABASE_ID },
      properties: {
        'Name': {
          title: [
            {
              text: {
                content: recipe.name
              }
            }
          ]
        },
        'Source URL': {
          url: recipe.url
        },
        'Tags': {
          multi_select: recipe.tags.map(tag => ({ name: tag }))
        },
        'Date Added': {
          date: {
            start: new Date().toISOString().split('T')[0]
          }
        }
      },
      children: [
        {
          object: 'block',
          type: 'heading_2',
          heading_2: {
            rich_text: [{ type: 'text', text: { content: 'Ingredients' } }]
          }
        },
        {
          object: 'block',
          type: 'paragraph',
          paragraph: {
            rich_text: [{ type: 'text', text: { content: recipe.ingredients } }]
          }
        },
        {
          object: 'block',
          type: 'heading_2',
          heading_2: {
            rich_text: [{ type: 'text', text: { content: 'Instructions' } }]
          }
        },
        {
          object: 'block',
          type: 'paragraph',
          paragraph: {
            rich_text: [{ 
              type: 'text', 
              text: { 
                content: recipe.instructions.substring(0, 2000) // Notion has limits
              } 
            }]
          }
        }
      ]
    });
    
    return { success: true, id: response.id };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// Main processing
async function main() {
  const batchDir = '/home/ubuntu/clawd/recipe-batch';
  const results = [];
  
  for (let i = 1; i <= 16; i++) {
    const num = String(i).padStart(2, '0');
    const transcriptPath = path.join(batchDir, `recipe_${num}_transcript.txt`);
    const urlPath = path.join(batchDir, `recipe_${num}_url.txt`);
    
    if (!fs.existsSync(transcriptPath) || !fs.existsSync(urlPath)) {
      console.log(`Recipe ${num}: Missing files, skipping`);
      results.push({ num, status: 'skipped', reason: 'missing files' });
      continue;
    }
    
    const transcript = fs.readFileSync(transcriptPath, 'utf8');
    const url = fs.readFileSync(urlPath, 'utf8').trim();
    
    // Skip if transcript is too short (likely not a recipe)
    if (transcript.length < 100) {
      console.log(`Recipe ${num}: Transcript too short, skipping`);
      results.push({ num, status: 'skipped', reason: 'no recipe content' });
      continue;
    }
    
    console.log(`Processing Recipe ${num}...`);
    const recipe = parseRecipe(transcript, url);
    console.log(`  Name: ${recipe.name.substring(0, 50)}...`);
    console.log(`  Tags: ${recipe.tags.join(', ')}`);
    
    const result = await saveRecipeToNotion(recipe);
    
    if (result.success) {
      console.log(`  ✓ Saved to Notion (ID: ${result.id})`);
      results.push({ num, status: 'success', id: result.id, name: recipe.name });
    } else {
      console.log(`  ✗ Failed: ${result.error}`);
      results.push({ num, status: 'failed', error: result.error });
    }
    
    // Rate limiting - wait 350ms between requests
    await new Promise(resolve => setTimeout(resolve, 350));
  }
  
  // Summary
  console.log('\n=== Summary ===');
  const successful = results.filter(r => r.status === 'success').length;
  const failed = results.filter(r => r.status === 'failed').length;
  const skipped = results.filter(r => r.status === 'skipped').length;
  
  console.log(`Total: 16`);
  console.log(`Successful: ${successful}`);
  console.log(`Failed: ${failed}`);
  console.log(`Skipped: ${skipped}`);
  
  if (failed > 0) {
    console.log('\nFailed recipes:');
    results.filter(r => r.status === 'failed').forEach(r => {
      console.log(`  Recipe ${r.num}: ${r.error}`);
    });
  }
  
  if (skipped > 0) {
    console.log('\nSkipped recipes:');
    results.filter(r => r.status === 'skipped').forEach(r => {
      console.log(`  Recipe ${r.num}: ${r.reason}`);
    });
  }
  
  // Save results to file
  fs.writeFileSync(
    path.join(batchDir, 'notion-results.json'),
    JSON.stringify(results, null, 2)
  );
  
  console.log('\nResults saved to notion-results.json');
}

main().catch(console.error);
