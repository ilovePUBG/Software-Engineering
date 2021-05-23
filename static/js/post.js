const loadFile = function (event) {
  const image = document.createElement("img");
  image.setAttribute("id", "output");
  image.setAttribute("src", URL.createObjectURL(event.target.files[0]));
  // console.log(event.target.files);
  image.setAttribute("width", "50px");
  image.setAttribute("height", "50px");
  const ctnr = document.querySelector(".image-display");
  ctnr.appendChild(image);
};
