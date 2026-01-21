/**
 * X-Style Clothing Recommender - Client App
 * 
 * Multi-Action Prediction 점수 시각화 및 사용자 행동 기록
 */

const API_BASE = '/api';

// State
let currentUserId = 'user_001';
let recommendations = [];
let userHistory = [];

// DOM Elements
const userSelect = document.getElementById('user-id');
const refreshBtn = document.getElementById('refresh-btn');
const clearHistoryBtn = document.getElementById('clear-history-btn');
const itemGrid = document.getElementById('item-grid');
const historyList = document.getElementById('history-list');
const currentUserEl = document.getElementById('current-user');
const historyCountEl = document.getElementById('history-count');
const recCountEl = document.getElementById('rec-count');
const toast = document.getElementById('toast');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  userSelect.value = currentUserId;
  loadRecommendations();
  loadHistory();

  userSelect.addEventListener('change', handleUserChange);
  refreshBtn.addEventListener('click', loadRecommendations);
  clearHistoryBtn.addEventListener('click', clearHistory);
});

// Event Handlers
function handleUserChange(e) {
  currentUserId = e.target.value;
  currentUserEl.textContent = userSelect.options[userSelect.selectedIndex].text.split(' (')[0];
  loadRecommendations();
  loadHistory();
}

// API Calls
async function loadRecommendations() {
  try {
    showLoading();

    const response = await fetch(`${API_BASE}/recommend?user_id=${currentUserId}&count=12`);
    const data = await response.json();

    if (data.status === 'success') {
      recommendations = data.recommendations;
      renderRecommendations();
      recCountEl.textContent = data.total;
      currentUserEl.textContent = userSelect.options[userSelect.selectedIndex].text.split(' (')[0];
    }
  } catch (error) {
    console.error('Failed to load recommendations:', error);
    showToast('추천을 불러오는데 실패했습니다');
  }
}

async function loadHistory() {
  try {
    const response = await fetch(`${API_BASE}/engagement/${currentUserId}/history`);
    const data = await response.json();

    if (data.status === 'success') {
      userHistory = data.history;
      renderHistory();
      historyCountEl.textContent = data.total;
    }
  } catch (error) {
    console.error('Failed to load history:', error);
  }
}

async function recordAction(itemId, actionType) {
  try {
    const response = await fetch(`${API_BASE}/engagement`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: currentUserId,
        item_id: itemId,
        action_type: actionType
      })
    });

    const data = await response.json();

    if (data.status === 'success') {
      showToast(`${getActionEmoji(actionType)} ${actionType} 기록됨`);
      loadHistory();

      // 1초 후 추천 새로고침
      setTimeout(loadRecommendations, 1000);
    }
  } catch (error) {
    console.error('Failed to record action:', error);
    showToast('행동 기록에 실패했습니다');
  }
}

async function clearHistory() {
  try {
    const response = await fetch(`${API_BASE}/engagement/${currentUserId}/history`, {
      method: 'DELETE'
    });

    const data = await response.json();

    if (data.status === 'success') {
      showToast('히스토리가 초기화되었습니다');
      loadHistory();
      loadRecommendations();
    }
  } catch (error) {
    console.error('Failed to clear history:', error);
  }
}

// Render Functions
function renderRecommendations() {
  if (recommendations.length === 0) {
    itemGrid.innerHTML = `
            <div class="empty-state">
                <p>추천 상품이 없습니다</p>
            </div>
        `;
    return;
  }

  itemGrid.innerHTML = recommendations.map(rec => createItemCard(rec)).join('');
}

function createItemCard(rec) {
  const { item, scores, final_score, diversity_penalty, source } = rec;

  const scoreEntries = [
    { label: 'Like', value: scores.like, positive: true },
    { label: 'Click', value: scores.click, positive: true },
    { label: 'Cart', value: scores.add_to_cart, positive: true },
    { label: 'Purchase', value: scores.purchase, positive: true },
    { label: 'Not Int.', value: scores.not_interested, positive: false },
  ];

  const scoreBars = scoreEntries.map(s => `
        <div class="score-bar">
            <span class="score-label">${s.label}</span>
            <div class="score-track">
                <div class="score-fill ${s.positive ? 'positive' : 'negative'}" 
                     style="width: ${Math.min(s.value * 100, 100)}%"></div>
            </div>
            <span class="score-value">${(s.value * 100).toFixed(0)}%</span>
        </div>
    `).join('');

  const tags = item.style_tags.map(tag => `<span class="tag">${tag}</span>`).join('');

  return `
        <div class="item-card">
            <img class="item-image" src="${item.image_url}" alt="${item.name}" 
                 onerror="this.src='https://via.placeholder.com/300x200?text=No+Image'">
            <div class="item-content">
                <div class="item-header">
                    <span class="item-brand">${item.brand}</span>
                    <span class="item-source ${source === 'in_network' ? 'in-network' : ''}">
                        ${source === 'in_network' ? '🎯 In-Network' : 'Out-of-Network'}
                    </span>
                </div>
                <h3 class="item-name">${item.name}</h3>
                <div class="item-price">₩${item.price.toLocaleString()}</div>
                <div class="item-tags">${tags}</div>
                
                <div class="scores-section">
                    <div class="scores-title">
                        <span>Multi-Action Scores</span>
                        <span class="final-score">Final: ${final_score.toFixed(2)}</span>
                    </div>
                    <div class="score-bars">
                        ${scoreBars}
                    </div>
                </div>
                
                <div class="action-buttons">
                    <button class="action-btn like" onclick="recordAction('${item.id}', 'like')">
                        ❤️ Like
                    </button>
                    <button class="action-btn click" onclick="recordAction('${item.id}', 'click')">
                        👆 Click
                    </button>
                    <button class="action-btn cart" onclick="recordAction('${item.id}', 'add_to_cart')">
                        🛒 Cart
                    </button>
                    <button class="action-btn not-interested" onclick="recordAction('${item.id}', 'not_interested')">
                        ✋ Not Int.
                    </button>
                </div>
            </div>
        </div>
    `;
}

function renderHistory() {
  if (userHistory.length === 0) {
    historyList.innerHTML = `
            <div class="empty-state">
                <p>아직 기록된 행동이 없습니다</p>
            </div>
        `;
    return;
  }

  // 최신순 정렬
  const sorted = [...userHistory].reverse();

  historyList.innerHTML = sorted.map(h => `
        <div class="history-item">
            <div class="history-action">
                <span class="history-action-type ${h.action_type}">
                    ${getActionEmoji(h.action_type)} ${h.action_type}
                </span>
                <span>→ ${h.item_id}</span>
            </div>
            <span class="history-time">${formatTime(h.timestamp)}</span>
        </div>
    `).join('');
}

// Utility Functions
function showLoading() {
  itemGrid.innerHTML = `
        <div class="loading" style="grid-column: 1 / -1;">
            <div class="spinner"></div>
        </div>
    `;
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');

  setTimeout(() => {
    toast.classList.remove('show');
  }, 2000);
}

function getActionEmoji(actionType) {
  const emojis = {
    'like': '❤️',
    'click': '👆',
    'add_to_cart': '🛒',
    'purchase': '💳',
    'share': '📤',
    'not_interested': '✋',
    'hide': '🙈'
  };
  return emojis[actionType] || '•';
}

function formatTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}
