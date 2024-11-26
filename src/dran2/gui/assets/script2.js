 const images=['/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d001_16h51m11s_HPN_RCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d001_16h51m11s_HPS_RCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d001_16h51m11s_HPS_LCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d001_16h51m11s_HPN_LCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d001_16h51m11s_ON_LCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d001_16h51m11s_ON_RCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d002_16h47m20s_ON_RCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d002_16h47m20s_ON_LCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d002_16h47m20s_HPS_RCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d002_16h47m20s_HPN_RCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d002_16h47m20s_HPN_LCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d002_16h47m20s_HPS_LCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d003_16h43m20s_ON_RCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d003_16h43m20s_ON_LCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d003_16h43m20s_HPS_RCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d003_16h43m20s_HPN_RCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d003_16h43m20s_HPN_LCP.png', '/Users/pfesesanivanzyl/dran/plots/JUPITER/22040/2024d003_16h43m20s_HPS_LCP.png'];
            const imagesPerPage = 20;
      let currentPage = 1;

      function displayImages(page) {
        const gallery = document.getElementById("image-gallery");
        gallery.innerHTML = "";

        const startIndex = (page - 1) * imagesPerPage;
        const endIndex = startIndex + imagesPerPage;

        for (let i = startIndex; i < endIndex && i < images.length; i++) {
          const img = document.createElement("img");
          img.src = images[i];
          gallery.appendChild(img);
        }
      }

      function buildPagination() {
        const pagination = document.getElementById("pagination");
        pagination.innerHTML = "";

        const totalPages = Math.ceil(images.length / imagesPerPage);

        for (let i = 1; i <= totalPages; i++) {
          const li = document.createElement("li");
          li.classList.add("page-item");
          const a = document.createElement("a");
          a.classList.add("page-link");
          a.href = "#";
          a.textContent = i;
          a.addEventListener("click", () => {
            currentPage = i;
            displayImages(currentPage);
            updateActivePage();
          });
          li.appendChild(a);
          pagination.appendChild(li);
        }
      }

      function updateActivePage() {
        const pagination = document.getElementById("pagination");
        const pageItems = pagination.querySelectorAll(".page-item");
        pageItems.forEach((item, index) => {
          if (index + 1 === currentPage) {
            item.classList.add("active");
          } else {
            item.classList.remove("active");
          }
        });
      }

      displayImages(currentPage);
      buildPagination();
      updateActivePage();

            