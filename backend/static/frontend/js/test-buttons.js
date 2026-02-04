/**
 * test-buttons.js
 * Script de prueba para verificar el estado de los botones del wizard
 */

(function() {
  console.log("=== PRUEBA DE BOTONES DEL WIZARD ===");
  
  const btnPrev = document.getElementById("btnPrev");
  const btnNext = document.getElementById("btnNext");
  const btnSave = document.getElementById("btnSave");
  
  console.log("\n1. Verificación de existencia:");
  console.log("btnPrev:", btnPrev);
  console.log("btnNext:", btnNext);
  console.log("btnSave:", btnSave);
  
  console.log("\n2. Estado de los botones:");
  if (btnPrev) {
    console.log("btnPrev.disabled:", btnPrev.disabled);
    console.log("btnPrev.onclick:", btnPrev.onclick);
    console.log("btnPrev.hasAttribute('onclick'):", btnPrev.hasAttribute('onclick'));
  }
  if (btnNext) {
    console.log("btnNext.disabled:", btnNext.disabled);
    console.log("btnNext.onclick:", btnNext.onclick);
    console.log("btnNext.hasAttribute('onclick'):", btnNext.hasAttribute('onclick'));
  }
  
  console.log("\n3. Prueba manual de click:");
  console.log("Para probar manualmente, ejecuta:");
  console.log("  document.getElementById('btnNext').click()");
  console.log("  document.getElementById('btnPrev').click()");
  
  console.log("\n4. Verificar event listeners (si está disponible):");
  if (typeof getEventListeners === 'function') {
    try {
      console.log("btnPrev listeners:", getEventListeners(btnPrev));
      console.log("btnNext listeners:", getEventListeners(btnNext));
    } catch (e) {
      console.log("getEventListeners no disponible (solo en Chrome DevTools)");
    }
  } else {
    console.log("getEventListeners no está disponible. Abre Chrome DevTools para usar esta función.");
  }
  
  console.log("\n5. Agregar listener de prueba:");
  if (btnNext) {
    btnNext.addEventListener("click", function testListener(e) {
      console.log("✅ LISTENER DE PRUEBA FUNCIONA! Click detectado en btnNext");
      alert("El botón Siguiente funciona! El listener de prueba detectó el click.");
    }, { once: true });
    console.log("✅ Listener de prueba agregado a btnNext. Haz click en el botón para probar.");
  }
  
  if (btnPrev) {
    btnPrev.addEventListener("click", function testListener(e) {
      console.log("✅ LISTENER DE PRUEBA FUNCIONA! Click detectado en btnPrev");
      alert("El botón Anterior funciona! El listener de prueba detectó el click.");
    }, { once: true });
    console.log("✅ Listener de prueba agregado a btnPrev. Haz click en el botón para probar.");
  }
  
  console.log("\n=== FIN DE PRUEBA ===");
  console.log("Si los listeners de prueba funcionan pero los botones no navegan, el problema está en setupNavigation()");
})();
