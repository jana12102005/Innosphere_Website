/* =====================================================
   InnoSphere — Premium Main JavaScript
   Clean, modular, production-ready
===================================================== */

/* =====================================================
   1. DOM READY WRAPPER
===================================================== */
document.addEventListener("DOMContentLoaded", function () {

    initNavbar();
    initDynamicFields();
    initDeleteConfirm();
    initCertForm();
    initEventForm();
    initTableSearch();
    initPageAnimations();

});

/* =====================================================
   2. NAVBAR — Active link highlight
===================================================== */
function initNavbar() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll(".navbar ul li a");

    navLinks.forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        }
    });
}

/* =====================================================
   3. ADMIN — Dynamic Event Form Builder
===================================================== */
function initDynamicFields() {
    const addFieldBtn     = document.getElementById("add-field-btn");
    const fieldsContainer = document.getElementById("dynamic-fields");

    if (!addFieldBtn || !fieldsContainer) return;

    addFieldBtn.addEventListener("click", function () {
        const div = document.createElement("div");
        div.className = "field-row";
        div.style.cssText = `
            display: flex;
            gap: 10px;
            align-items: center;
            margin-bottom: 10px;
            animation: msg-in 0.2s ease;
        `;

        div.innerHTML = `
            <input
                type="text"
                name="field_name"
                placeholder="Enter question / field name"
                required
                style="flex:1"
            />
            <button type="button" class="btn btn-danger remove-field-btn" style="white-space:nowrap">
                Remove
            </button>
        `;

        fieldsContainer.appendChild(div);

        // Focus the new input
        div.querySelector("input").focus();
    });

    // Remove field (event delegation)
    fieldsContainer.addEventListener("click", function (e) {
        if (e.target.classList.contains("remove-field-btn")) {
            const row = e.target.closest(".field-row");
            row.style.opacity = "0";
            row.style.transform = "translateX(10px)";
            row.style.transition = "all 0.2s ease";
            setTimeout(() => row.remove(), 200);
        }
    });
}

/* =====================================================
   4. ADMIN — Delete Confirm
===================================================== */
function initDeleteConfirm() {
    document.querySelectorAll(".delete-btn").forEach(btn => {
        btn.addEventListener("click", function (e) {
            if (!confirm("Are you sure you want to delete this item? This action cannot be undone.")) {
                e.preventDefault();
            }
        });
    });
}

/* =====================================================
   5. CERTIFICATE FORM — Loading State
===================================================== */
function initCertForm() {
    const certForm = document.getElementById("certificate-form");

    if (!certForm) return;

    certForm.addEventListener("submit", function () {
        const btn = certForm.querySelector("button[type='submit']");
        if (btn) {
            btn.innerHTML = `
                <span style="display:inline-flex;align-items:center;gap:8px">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                        <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                    </svg>
                    Generating Certificate...
                </span>
            `;
            btn.disabled = true;
            btn.style.opacity = "0.8";
        }
    });
}

/* =====================================================
   6. EVENT REGISTRATION — Validation
===================================================== */
function initEventForm() {
    const eventForm = document.getElementById("event-registration-form");

    if (!eventForm) return;

    eventForm.addEventListener("submit", function (e) {
        const email   = eventForm.querySelector("input[name='email']");
        const phone   = eventForm.querySelector("input[name='contact']");
        let   isValid = true;

        // Clear previous errors
        eventForm.querySelectorAll(".field-error").forEach(el => el.remove());
        eventForm.querySelectorAll(".input-error").forEach(el => {
            el.style.borderColor = "";
        });

        // Email check
        if (email && !email.value.includes("@")) {
            showFieldError(email, "Please enter a valid email address.");
            isValid = false;
        }

        // Phone check (optional field — only validate if filled)
        if (phone && phone.value && !/^\d{10}$/.test(phone.value.trim())) {
            showFieldError(phone, "Enter a valid 10-digit mobile number.");
            isValid = false;
        }

        if (!isValid) e.preventDefault();
    });
}

function showFieldError(input, message) {
    input.style.borderColor = "#e74c3c";
    input.style.boxShadow   = "0 0 0 3px rgba(231,76,60,0.12)";

    const err = document.createElement("span");
    err.className   = "field-error";
    err.textContent = message;
    err.style.cssText = `
        display: block;
        font-size: 12px;
        color: #c0392b;
        margin-top: 4px;
        font-weight: 500;
    `;

    input.parentNode.insertBefore(err, input.nextSibling);
    input.focus();
}

/* =====================================================
   7. ADMIN TABLE — Live Search Filter
===================================================== */
function initTableSearch() {
    const searchInput = document.getElementById("table-search");
    const tableBody   = document.querySelector("table tbody");

    if (!searchInput || !tableBody) return;

    searchInput.addEventListener("input", function () {
        const query = this.value.toLowerCase().trim();
        const rows  = tableBody.querySelectorAll("tr");

        rows.forEach(row => {
            const text    = row.textContent.toLowerCase();
            const matches = text.includes(query);
            row.style.display = matches ? "" : "none";
        });

        // Show empty state
        const visible = [...rows].filter(r => r.style.display !== "none");
        const existing = tableBody.querySelector(".empty-search");

        if (visible.length === 0 && !existing) {
            const emptyRow = document.createElement("tr");
            emptyRow.className = "empty-search";
            emptyRow.innerHTML = `
                <td colspan="20" style="text-align:center;padding:32px;color:#718096;font-style:italic">
                    No results found for "<strong>${escapeHtml(query)}</strong>"
                </td>
            `;
            tableBody.appendChild(emptyRow);
        } else if (visible.length > 0 && existing) {
            existing.remove();
        }
    });
}

function escapeHtml(str) {
    return str.replace(/[&<>"']/g, m => ({
        '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
    }[m]));
}

/* =====================================================
   8. PAGE ANIMATIONS — Scroll reveal
===================================================== */
function initPageAnimations() {
    // Staggered card entrance on load
    const cards = document.querySelectorAll(".card, .grid-item, .dashboard-card, .polaroid");

    cards.forEach((card, i) => {
        card.style.opacity   = "0";
        card.style.transform = "translateY(18px)";
        card.style.transition = `opacity 0.4s ease ${i * 60}ms, transform 0.4s ease ${i * 60}ms`;

        setTimeout(() => {
            card.style.opacity   = "1";
            card.style.transform = "translateY(0)";
        }, 80 + i * 60);
    });

    // Intersection Observer for below-fold elements
    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("revealed");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12 });

        document.querySelectorAll(".reveal-on-scroll").forEach(el => {
            el.style.opacity   = "0";
            el.style.transform = "translateY(20px)";
            el.style.transition = "opacity 0.5s ease, transform 0.5s ease";
            observer.observe(el);
        });
    }
}

// CSS class trigger for IntersectionObserver
const style = document.createElement("style");
style.textContent = `.revealed { opacity: 1 !important; transform: none !important; }`;
document.head.appendChild(style);


/* =====================================================
   CHAT WITH INNO — Full Chat System
===================================================== */

/* -----------------------------------------------
   Open / Close chat widget
----------------------------------------------- */
function openInnoChat() {
    const chatBox = document.getElementById("inno-chat-box");
    const overlay = document.getElementById("inno-chat-overlay");
    if (!chatBox || !overlay) return;

    overlay.style.display = "block";
    chatBox.style.display = "flex";

    // Animate in
    chatBox.style.opacity   = "0";
    chatBox.style.transform = "scale(0.96) translateY(10px)";
    chatBox.style.transition = "opacity 0.25s ease, transform 0.25s ease";

    requestAnimationFrame(() => {
        chatBox.style.opacity   = "1";
        chatBox.style.transform = "scale(1) translateY(0)";
    });
}

function closeInnoChat() {
    const chatBox = document.getElementById("inno-chat-box");
    const overlay = document.getElementById("inno-chat-overlay");
    if (!chatBox || !overlay) return;

    chatBox.style.opacity   = "0";
    chatBox.style.transform = "scale(0.96) translateY(10px)";

    setTimeout(() => {
        overlay.style.display = "none";
        chatBox.style.display = "none";
    }, 220);
}

/* -----------------------------------------------
   Start chat (welcome → chat screen)
----------------------------------------------- */
function startChat() {
    const welcome = document.getElementById("inno-chat-welcome");
    const content = document.getElementById("inno-chat-content");
    if (!welcome || !content) return;

    welcome.style.opacity   = "0";
    welcome.style.transform = "translateY(-10px)";
    welcome.style.transition = "all 0.2s ease";

    setTimeout(() => {
        welcome.classList.add("hidden");
        content.classList.remove("hidden");
        content.style.opacity   = "0";
        content.style.transform = "translateY(10px)";
        content.style.transition = "all 0.25s ease";

        requestAnimationFrame(() => {
            content.style.opacity   = "1";
            content.style.transform = "translateY(0)";
        });

        addBotMessage("👋 Hello! I'm Inno, your InnoSphere assistant. How can I help you today?");
    }, 200);
}

/* -----------------------------------------------
   Add bot message
----------------------------------------------- */
function addBotMessage(text) {
    const box = document.getElementById("inno-chat-messages");
    if (!box) return;

    const div = document.createElement("div");
    div.className   = "inno-msg bot";
    div.textContent = text;

    box.appendChild(div);
    scrollToBottom(box);
}

/* -----------------------------------------------
   Add user message
----------------------------------------------- */
function addUserMessage(text) {
    const box = document.getElementById("inno-chat-messages");
    if (!box) return;

    const div = document.createElement("div");
    div.className   = "inno-msg user";
    div.textContent = text;

    box.appendChild(div);
    scrollToBottom(box);
}

/* -----------------------------------------------
   Typing indicator
----------------------------------------------- */
function addTypingIndicator() {
    const box = document.getElementById("inno-chat-messages");
    if (!box) return;

    const div = document.createElement("div");
    div.className = "inno-msg bot typing-indicator";
    div.id        = "typing-bubble";
    div.innerHTML = `
        <span style="display:inline-flex;gap:4px;align-items:center;padding:2px 0">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
        </span>
    `;

    // Dot animation styles (injected once)
    if (!document.getElementById("dot-style")) {
        const s = document.createElement("style");
        s.id = "dot-style";
        s.textContent = `
            .dot {
                width: 7px; height: 7px;
                border-radius: 50%;
                background: #b8923a;
                animation: dot-bounce 1.2s infinite ease-in-out;
            }
            .dot:nth-child(2) { animation-delay: 0.2s; }
            .dot:nth-child(3) { animation-delay: 0.4s; }
            @keyframes dot-bounce {
                0%, 80%, 100% { transform: translateY(0); opacity: 0.5; }
                40%           { transform: translateY(-6px); opacity: 1; }
            }
        `;
        document.head.appendChild(s);
    }

    box.appendChild(div);
    scrollToBottom(box);
}

function removeTypingIndicator() {
    const bubble = document.getElementById("typing-bubble");
    if (bubble) bubble.remove();
}

/* -----------------------------------------------
   Send message to backend
----------------------------------------------- */
function sendInnoMessage() {
    const input = document.getElementById("inno-user-input");
    if (!input) return;

    const msg = input.value.trim();
    if (!msg) return;

    addUserMessage(msg);
    input.value = "";

    addTypingIndicator();

    fetch("/chat/api", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg })
    })
    .then(res => res.json())
    .then(data => {
        removeTypingIndicator();
        addBotMessage(data.reply || "Sorry, I didn't get a response.");
    })
    .catch(() => {
        removeTypingIndicator();
        addBotMessage("⚠️ Connection issue — please try again in a moment.");
    });
}

/* -----------------------------------------------
   Scroll to bottom helper
----------------------------------------------- */
function scrollToBottom(box) {
    setTimeout(() => {
        box.scrollTo({ top: box.scrollHeight, behavior: "smooth" });
    }, 40);
}

/* -----------------------------------------------
   Enter key support
----------------------------------------------- */
document.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        const input = document.getElementById("inno-user-input");
        if (input && document.activeElement === input) {
            sendInnoMessage();
        }
    }
});

