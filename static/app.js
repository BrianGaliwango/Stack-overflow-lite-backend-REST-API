const menu_btn = document.querySelector('.menu-button');
const options_container = document.querySelector('.options-container');

menu_btn.addEventListener('click', () => {
  options_container.classList.toggle('hide')
})
