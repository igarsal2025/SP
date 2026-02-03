#!/usr/bin/env node
/**
 * Script para verificar budget de performance
 * Verifica FCP, TTI y tamaño de JS inicial
 */

const fs = require("fs");
const path = require("path");

const PERFORMANCE_BUDGET = {
  FCP: 1000, // First Contentful Paint en ms
  TTI: 2500, // Time to Interactive en ms
  JS_INITIAL: 100 * 1024, // 100KB en bytes
};

function getFileSize(filePath) {
  try {
    const stats = fs.statSync(filePath);
    return stats.size;
  } catch (error) {
    return 0;
  }
}

function checkJSBundleSize() {
  const jsDir = path.join(__dirname, "../backend/static/frontend/js");
  const jsFiles = ["wizard.js", "pwa.js", "sync.js", "analytics.js"];
  
  let totalSize = 0;
  const fileSizes = {};
  
  jsFiles.forEach((file) => {
    const filePath = path.join(jsDir, file);
    const size = getFileSize(filePath);
    fileSizes[file] = size;
    totalSize += size;
  });
  
  console.log("\n📦 JavaScript Bundle Size:");
  console.log("─".repeat(50));
  jsFiles.forEach((file) => {
    const size = fileSizes[file];
    const sizeKB = (size / 1024).toFixed(2);
    console.log(`  ${file.padEnd(20)} ${sizeKB.padStart(8)} KB`);
  });
  
  const totalKB = (totalSize / 1024).toFixed(2);
  const limitKB = (PERFORMANCE_BUDGET.JS_INITIAL / 1024).toFixed(2);
  
  console.log("─".repeat(50));
  console.log(`  Total: ${totalKB.padStart(8)} KB / ${limitKB} KB`);
  
  if (totalSize > PERFORMANCE_BUDGET.JS_INITIAL) {
    console.error(`\n❌ ERROR: JS bundle size (${totalKB} KB) exceeds limit (${limitKB} KB)`);
    return false;
  }
  
  console.log(`\n✓ JS bundle size within limits`);
  return true;
}

function checkPerformanceMetrics() {
  console.log("\n⚡ Performance Budget Check");
  console.log("=".repeat(50));
  console.log("\n📊 Budget Limits:");
  console.log(`  FCP:  < ${PERFORMANCE_BUDGET.FCP}ms`);
  console.log(`  TTI:  < ${PERFORMANCE_BUDGET.TTI}ms`);
  console.log(`  JS:   < ${PERFORMANCE_BUDGET.JS_INITIAL / 1024}KB`);
  
  const jsCheck = checkJSBundleSize();
  
  console.log("\n" + "=".repeat(50));
  console.log("\n💡 Note: FCP and TTI metrics require Lighthouse CI");
  console.log("   Run: npm install -g @lhci/cli && lhci autorun");
  
  return jsCheck;
}

// Ejecutar verificación
if (require.main === module) {
  const success = checkPerformanceMetrics();
  process.exit(success ? 0 : 1);
}

module.exports = { checkPerformanceMetrics, PERFORMANCE_BUDGET };
