/*
 * paper-follow.js — 纸面随光标移动
 * ---------------------------------------------------------------------------
 * 端口与主页（homepage_repo/assets/js/fix_flash_and_pointer.py）同款：
 *   pointermove → rAF 节流 → 写 --paper-px / --paper-py
 * 主题 CSS 用这两个变量做 background-position 视差（b 层 1.6× 深度）。
 *
 * 注入方式：Typora 只加载主题 CSS，读不到指针位置，因此由外部注入器
 * （同目录 inject.py，走 Chrome DevTools 协议，不修改 Typora 本体）注入本页。
 * 脚本可重复注入：有 __paperFollowInstalled 守卫。
 */
(function () {
  'use strict';

  if (window.__paperFollowInstalled) return;
  window.__paperFollowInstalled = true;

  // 用户要求减少动态时不做视差
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return;
  }

  var root = document.documentElement;
  var AMP = 26;                 // 最大位移 px（与主页一致）
  var raf = 0, tx = 0, ty = 0;

  function apply() {
    raf = 0;
    root.style.setProperty('--paper-px', tx.toFixed(1) + 'px');
    root.style.setProperty('--paper-py', ty.toFixed(1) + 'px');
  }

  function onMove(e) {
    tx = (e.clientX / window.innerWidth - 0.5) * -2 * AMP;
    ty = (e.clientY / window.innerHeight - 0.5) * -2 * AMP;
    if (!raf) raf = window.requestAnimationFrame(apply);
  }

  window.addEventListener('pointermove', onMove, { passive: true });
})();
