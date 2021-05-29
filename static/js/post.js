const loadFile = function (event) {

  const images = event.target.files;
  const ctnr = document.querySelector(".image-display");
  let img;
  // console.log(images.length);

  for (let i = 0; i < images.length; i++) {
    img = document.createElement("img");

    img.setAttribute("id", "output");
    img.setAttribute("class", "rounded");
    img.setAttribute("src", URL.createObjectURL(images[i]));
    img.setAttribute("width", "150px");
    img.setAttribute("height", "150px");
    img.setAttribute("name", "image");

    ctnr.appendChild(img);
  }
};
