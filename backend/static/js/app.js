const API = '/api';

// --- Pantry Page ---
const pantryBody = document.getElementById('pantry-body');
const addBtn = document.getElementById('add-btn');
const cancelBtn = document.getElementById('cancel-btn');
const addForm = document.getElementById('add-form');
const pantryForm = document.getElementById('pantry-form');
const searchInput = document.getElementById('search');
const categoryFilter = document.getElementById('category-filter');

let editingId = null;

async function fetchPantry(params = {}) {
    const qs = new URLSearchParams(params).toString();
    const res = await fetch(`${API}/pantry${qs ? '?' + qs : ''}`);
    return res.json();
}

async function renderPantry() {
    if (!pantryBody) return;
    const params = {};
    if (searchInput?.value) params.search = searchInput.value;
    if (categoryFilter?.value) params.category = categoryFilter.value;

    const items = await fetchPantry(params);
    const categories = new Set();

    pantryBody.innerHTML = items.map(item => {
        if (item.category) categories.add(item.category);
        return `<tr>
            <td>${esc(item.name)}</td>
            <td>${item.quantity ?? ''}</td>
            <td>${esc(item.unit ?? '')}</td>
            <td>${esc(item.category ?? '')}</td>
            <td>${esc(item.notes ?? '')}</td>
            <td>
                <button class="btn" onclick="editItem(${item.id})">Edit</button>
                <button class="btn btn-danger" onclick="deleteItem(${item.id})">Del</button>
            </td>
        </tr>`;
    }).join('');

    // Populate category filter
    if (categoryFilter) {
        const current = categoryFilter.value;
        const opts = ['<option value="">All Categories</option>'];
        for (const c of [...categories].sort()) {
            opts.push(`<option value="${esc(c)}" ${c === current ? 'selected' : ''}>${esc(c)}</option>`);
        }
        categoryFilter.innerHTML = opts.join('');
    }
}

if (addBtn) addBtn.addEventListener('click', () => {
    editingId = null;
    pantryForm.reset();
    addForm.classList.remove('hidden');
});
if (cancelBtn) cancelBtn.addEventListener('click', () => addForm.classList.add('hidden'));

if (pantryForm) pantryForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(pantryForm);
    const body = {
        name: fd.get('name'),
        quantity: fd.get('quantity') ? parseFloat(fd.get('quantity')) : null,
        unit: fd.get('unit') || null,
        category: fd.get('category') || null,
        notes: fd.get('notes') || null,
    };
    const method = editingId ? 'PUT' : 'POST';
    const url = editingId ? `${API}/pantry/${editingId}` : `${API}/pantry`;
    await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    addForm.classList.add('hidden');
    pantryForm.reset();
    editingId = null;
    renderPantry();
});

window.editItem = async function(id) {
    const res = await fetch(`${API}/pantry/${id}`);
    const item = await res.json();
    editingId = id;
    pantryForm.name.value = item.name;
    pantryForm.quantity.value = item.quantity ?? '';
    pantryForm.unit.value = item.unit ?? '';
    pantryForm.category.value = item.category ?? '';
    pantryForm.notes.value = item.notes ?? '';
    addForm.classList.remove('hidden');
};

window.deleteItem = async function(id) {
    if (!confirm('Delete this item?')) return;
    await fetch(`${API}/pantry/${id}`, { method: 'DELETE' });
    renderPantry();
};

if (searchInput) searchInput.addEventListener('input', debounce(renderPantry, 300));
if (categoryFilter) categoryFilter.addEventListener('change', renderPantry);

// --- Upload Page ---
const uploadForm = document.getElementById('upload-form');
if (uploadForm) uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitBtn = uploadForm.querySelector('button[type="submit"]');
    const result = document.getElementById('upload-result');
    const list = document.getElementById('detected-items');
    const errorDiv = document.getElementById('upload-error');

    // Show loading state
    submitBtn.disabled = true;
    submitBtn.textContent = 'Analyzing…';
    result.classList.add('hidden');
    if (errorDiv) errorDiv.classList.add('hidden');

    try {
        const fd = new FormData(uploadForm);
        const res = await fetch(`${API}/photos/upload`, { method: 'POST', body: fd });
        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.detail || `Upload failed (${res.status})`);
        }

        if (data.items.length === 0) {
            list.innerHTML = `<li class="text-muted">${esc(data.message)}</li>`;
        } else {
            list.innerHTML = data.items.map(i =>
                `<li>${esc(i.name)}${i.quantity ? ' — ' + i.quantity + ' ' + (i.unit || '') : ''}${i.category ? ' <span class="tag">' + esc(i.category) + '</span>' : ''}</li>`
            ).join('');
        }
        result.classList.remove('hidden');

        document.getElementById('add-all-btn').onclick = async () => {
            await fetch(`${API}/pantry/bulk`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data.items),
            });
            alert('Items added to pantry!');
        };
    } catch (err) {
        if (errorDiv) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        } else {
            alert(err.message);
        }
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Upload & Detect';
    }
});

// --- Helpers ---
function esc(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
}

function debounce(fn, ms) {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

// Init
renderPantry();
