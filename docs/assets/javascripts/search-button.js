// The search box on the home page is a real button, so it can be reached with Tab
// and activated with Enter or Space; it opens Material's search overlay.
document.addEventListener("click", (event) => {
  if (!event.target.closest("[data-cs-search]")) return;
  const toggle = document.getElementById("__search");
  if (!toggle) return;
  toggle.checked = true;
  toggle.dispatchEvent(new Event("change"));
  document.querySelector(".md-search__input")?.focus();
});
