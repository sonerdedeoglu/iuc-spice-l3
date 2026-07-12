const state = {
  root: null,
  pagesById: new Map(),
  selectedPageId: null,
  expanded: new Set(),
  query: "",
};

const treeRoot = document.getElementById("treeRoot");
const searchInput = document.getElementById("searchInput");
const pageTitle = document.getElementById("pageTitle");
const pageFrame = document.getElementById("pageFrame");
const openPreview = document.getElementById("openPreview");
const openStorage = document.getElementById("openStorage");

async function init() {
  const response = await fetch("pages.json", { cache: "no-store" });

  if (!response.ok) {
    throw new Error("pages.json yüklenemedi");
  }

  const data = await response.json();
  state.root = data.tree;
  indexPages(state.root);
  expandInitialPath(state.root);
  renderTree();
  selectPage(state.root.page_id);
}

function indexPages(page) {
  if (!page || !page.page_id) {
    return;
  }

  state.pagesById.set(page.page_id, page);

  for (const child of page.children || []) {
    indexPages(child);
  }
}

function expandInitialPath(page) {
  if (!page) {
    return;
  }

  state.expanded.add(page.page_id);
}

function renderTree() {
  treeRoot.innerHTML = "";

  if (!state.root) {
    treeRoot.innerHTML = '<div class="empty-state">Sayfa ağacı bulunamadı.</div>';
    return;
  }

  const node = renderNode(state.root);

  if (node) {
    treeRoot.appendChild(node);
  } else {
    treeRoot.innerHTML = '<div class="empty-state">Arama sonucu bulunamadı.</div>';
  }
}

function renderNode(page) {
  const children = page.children || [];
  const matchingChildren = children
    .map(renderNode)
    .filter(Boolean);
  const selfMatches = matchesQuery(page);

  if (state.query && !selfMatches && matchingChildren.length === 0) {
    return null;
  }

  if (state.query && matchingChildren.length > 0) {
    state.expanded.add(page.page_id);
  }

  const node = document.createElement("div");
  node.className = "tree-node";

  if (!state.expanded.has(page.page_id)) {
    node.classList.add("is-collapsed");
  }

  const row = document.createElement("div");
  row.className = "tree-row";

  if (page.page_id === state.selectedPageId) {
    row.classList.add("is-selected");
  }

  const toggle = document.createElement("button");
  toggle.className = "toggle";
  toggle.type = "button";
  toggle.textContent = state.expanded.has(page.page_id) ? "▾" : "▸";
  toggle.disabled = children.length === 0;
  toggle.title = state.expanded.has(page.page_id) ? "Daralt" : "Genişlet";
  toggle.addEventListener("click", () => {
    toggleExpanded(page.page_id);
  });

  const link = document.createElement("button");
  link.className = "page-link";
  link.type = "button";
  link.textContent = page.title;
  link.title = page.title;
  link.addEventListener("click", () => {
    selectPage(page.page_id);
  });

  row.appendChild(toggle);
  row.appendChild(link);
  node.appendChild(row);

  if (matchingChildren.length > 0) {
    const childrenContainer = document.createElement("div");
    childrenContainer.className = "tree-children";

    for (const childNode of matchingChildren) {
      childrenContainer.appendChild(childNode);
    }

    node.appendChild(childrenContainer);
  }

  return node;
}

function matchesQuery(page) {
  if (!state.query) {
    return true;
  }

  return normalize(page.title).includes(state.query);
}

function normalize(value) {
  return String(value || "")
    .toLocaleLowerCase("tr-TR")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

function toggleExpanded(pageId) {
  if (state.expanded.has(pageId)) {
    state.expanded.delete(pageId);
  } else {
    state.expanded.add(pageId);
  }

  renderTree();
}

function selectPage(pageId) {
  const page = state.pagesById.get(pageId);

  if (!page) {
    return;
  }

  state.selectedPageId = pageId;
  state.expanded.add(pageId);
  pageTitle.textContent = page.title;
  pageFrame.src = page.view_file;
  openPreview.href = page.view_file;
  openStorage.href = page.storage_file;
  renderTree();
}

searchInput.addEventListener("input", () => {
  state.query = normalize(searchInput.value.trim());
  renderTree();
});

init().catch((error) => {
  treeRoot.innerHTML = `<div class="empty-state">${error.message}</div>`;
  pageTitle.textContent = "Viewer yüklenemedi";
});
