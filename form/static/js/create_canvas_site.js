const createCanvasSiteButton = document.getElementById(
  "create_canvas_site_button"
);
createCanvasSiteButton.addEventListener("click", (event) => {
  const loadingText = document.getElementById("id_creating_canvas_site");
  loadingText.style.display = "block";
  createCanvasSiteButton.style.display = "none";
});
