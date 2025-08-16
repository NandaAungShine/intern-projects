// Hero Section rotation
const heroSection = document.getElementById('heroSection');
const heading = document.getElementById('heading');
const ppppp = document.getElementById('paragraph');

// Replace these with your actual image URLs
const backgrounds = [
    'url("Img/bagan.jpg")',
    'url("Img/mountain.jpg")',
    'url("Img/ocean.jpg")'
];

const headings = [
    'BAGAN',
    'TAUNGGYI',
    'NGAPALI'
];

const paras = [
    'Mandalay Division , Myanmar',
    'Shan State , Myanmar',
    'Rakhine State , Myanmar'
];

let currentIndex = 0;

// Set initial background
heroSection.style.backgroundImage = backgrounds[currentIndex];
heading.innerHTML = headings[currentIndex];
ppppp.innerHTML = paras[currentIndex];

// Automatic background rotation
setInterval(() => {
    currentIndex = (currentIndex + 1) % backgrounds.length;
    heroSection.style.backgroundImage = backgrounds[currentIndex];
    heading.innerHTML = headings[currentIndex];
    ppppp.innerHTML = paras[currentIndex];
}, 10000); // every 10 seconds

// Manual controls
function nextImage() {
    currentIndex = (currentIndex + 1) % backgrounds.length;
    heroSection.style.backgroundImage = backgrounds[currentIndex];
    heading.innerHTML = headings[currentIndex];
    ppppp.innerHTML = paras[currentIndex];
}

function prevImage() {
    currentIndex = (currentIndex - 1 + backgrounds.length) % backgrounds.length;
    heroSection.style.backgroundImage = backgrounds[currentIndex];
    heading.innerHTML = headings[currentIndex];
    ppppp.innerHTML = paras[currentIndex];
}


// top-destionations
document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.cardo');

    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.width = '270px';
            card.style.height = '350px';
            card.style.transform = 'translateY(-25px)';

        });

        card.addEventListener('mouseleave', () => {
            card.style.width = '110px';
            card.style.height = '300px';
            card.style.transform = 'translateY(0)';

        });
    });
});



// 5. Booking Form - Explore Packages vs. Customize Your Trip (Image 2 & 3)
const explorePackageBtn = document.querySelector('.search-options button:nth-child(1)');
const customizeTripBtn = document.querySelector('.search-options button:nth-child(2)');
const exploreForm = document.querySelector('.booking-form-container .form-inputs');
const customizeForm = document.querySelector('.booking-form-container .customize-form-inputs');
const bookingTabs = document.querySelector('.booking-form-container .tabs');
const promoCodeInput = document.querySelector('.booking-form-container .promo-code');
const searchButton = document.querySelector('.booking-form-container .search-btn');

if (explorePackageBtn && customizeTripBtn && exploreForm && customizeForm) {
    explorePackageBtn.addEventListener('click', () => {
        explorePackageBtn.classList.add('active');
        customizeTripBtn.classList.remove('active');
        exploreForm.style.display = 'grid'; // Show as grid
        customizeForm.style.display = 'none'; // Hide
        bookingTabs.style.display = 'flex'; // Show tabs
        if (promoCodeInput) promoCodeInput.style.display = 'block';
        if (searchButton) searchButton.style.display = 'block';

    });

    customizeTripBtn.addEventListener('click', () => {
        customizeTripBtn.classList.add('active');
        explorePackageBtn.classList.remove('active');
        exploreForm.style.display = 'none'; // Hide
        customizeForm.style.display = 'grid'; // Show as grid
        bookingTabs.style.display = 'none'; // Hide tabs
        if (promoCodeInput) promoCodeInput.style.display = 'none';
        if (searchButton) searchButton.style.display = 'none';

    });
}

// Initialize the correct form on page load
explorePackageBtn.click(); // Default to "Explore Our Packages"





document.addEventListener('DOMContentLoaded', function () {
    let currentReviewIndex = 0;
    let reviewsPerView = 3;
    const reviewsCarousel = document.getElementById('reviewsCarousel');
    const reviewsCarouselInner = reviewsCarousel.querySelector('.carousel-inner');
    const reviewItems = reviewsCarouselInner.querySelectorAll('.carousel-item');
    const reviewsPrevBtn = reviewsCarousel.querySelector('.carousel-control-prev');
    const reviewsNextBtn = reviewsCarousel.querySelector('.carousel-control-next');

    function initReviewsCarousel() {
        function calculateReviewsPerView() {
            if (window.innerWidth <= 768) return 1;
            if (window.innerWidth <= 992) return 2;
            return 3;
        }

        function updateCarouselPosition() {
            const itemWidth = reviewItems[0].offsetWidth;
            const gap = 20;
            const newPosition = currentReviewIndex * (itemWidth + gap);

            reviewsCarouselInner.style.transform = `translateX(-${newPosition}px)`;
            reviewsCarouselInner.style.transition = 'transform 0.5s ease';

            reviewsPrevBtn.style.display = currentReviewIndex <= 0 ? 'none' : 'block';
            reviewsNextBtn.style.display = currentReviewIndex >= reviewItems.length - reviewsPerView ? 'none' : 'block';
        }

        function nextSlide() {
            if (currentReviewIndex < reviewItems.length - reviewsPerView) {
                currentReviewIndex++;
                updateCarouselPosition();
            }
        }

        function prevSlide() {
            if (currentReviewIndex > 0) {
                currentReviewIndex--;
                updateCarouselPosition();
            }
        }

        reviewsPrevBtn.addEventListener('click', prevSlide);
        reviewsNextBtn.addEventListener('click', nextSlide);

        window.addEventListener('resize', function () {
            reviewsPerView = calculateReviewsPerView();
            updateCarouselPosition();
        });

        reviewsPerView = calculateReviewsPerView();
        updateCarouselPosition();

        let touchStartX = 0;
        let touchEndX = 0;

        reviewsCarouselInner.addEventListener('touchstart', function (e) {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        reviewsCarouselInner.addEventListener('touchend', function (e) {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, { passive: true });

        document.getElementById('reviewForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // 1. Get form values
    const rating = document.querySelector('input[name="rating"]:checked').value;
    const reviewText = document.getElementById('reviewText').value;
    const reviewerName = document.getElementById('reviewerName').value;
    const reviewerUsername = reviewerName.toLowerCase().replace(/\s+/g, '') + Math.floor(Math.random() * 1000);
    
    // 2. Create new review card HTML
    const stars = '★'.repeat(rating) + '☆'.repeat(5 - rating);
    const newReview = `
        <div class="carousel-item">
            <div class="review-card">
                <div class="review-text">"${reviewText}"</div>
                <div class="review-stars">${stars}</div>
                <div class="reviewer">
                    <div class="reviewer-avatar" style="background-image: url('Img/default-avatar.png');"></div>
                    <div class="reviewer-info">
                        <div class="reviewer-name">${reviewerName}</div>
                        <div class="reviewer-username">@${reviewerUsername}</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    const carouselInner = document.getElementById('reviews-carousel-inner');
    carouselInner.insertAdjacentHTML('beforeend', newReview);
    
    this.reset();
    
    alert('Thank you for your review! It will appear in our testimonials.');
});

        function handleSwipe() {
            const swipeThreshold = 50;

            if (touchStartX - touchEndX > swipeThreshold) {
                nextSlide();
            } else if (touchEndX - touchStartX > swipeThreshold) {
                prevSlide();
            }
        }
    }

    const reviewForm = document.getElementById('reviewForm');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const reviewText = document.getElementById('reviewText').value;
            const reviewerName = document.getElementById('reviewerName').value;
            const reviewerEmail = document.getElementById('reviewerEmail').value;
            const ratingInput = document.querySelector('input[name="rating"]:checked');

            if (!reviewText.trim() || !reviewerName.trim() || !reviewerEmail.trim() || !ratingInput) {
                alert('Please fill in all fields (Review, Name, Email) and select a rating.');
                return;
            }

            const ratingValue = parseInt(ratingInput.value);

            const starsHtml = '★'.repeat(ratingValue) + '☆'.repeat(5 - ratingValue);

            const nameParts = reviewerName.split(' ');
            const avatarText = nameParts.length > 1
                ? `${nameParts[0][0]}${nameParts[nameParts.length - 1][0]}`.toUpperCase()
                : reviewerName.substring(0, 2).toUpperCase();

            const newReviewCardHTML = `
                <div class="carousel-item">
                    <div class="review-card">
                        <div class="review-text">"${reviewText}"</div>
                        <div class="review-stars">${starsHtml}</div>
                        <div class="reviewer">
                            <div class="reviewer-avatar" style="background-image: url('https://via.placeholder.com/50x50/007bff/ffffff?text=${avatarText}');"></div>
                            <div class="reviewer-info">
                                <div class="reviewer-name">${reviewerName}</div>
                                <div class="reviewer-username">@${reviewerName.replace(/\s+/g, '').toLowerCase()}</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            reviewsCarouselInner.insertAdjacentHTML('afterbegin', newReviewCard);

            reviewForm.reset();

            alert('Thank you for your review! Your feedback has been added.');

            currentReviewIndex = 0;
            const updatedReviewItems = reviewsCarouselInner.querySelectorAll('.carousel-item');
            updateCarouselPosition();
        });
    }

    if (reviewsCarousel && reviewItems.length > 0) {
        initReviewsCarousel();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const faqQuestions = document.querySelectorAll('.faq-question');
    
    faqQuestions.forEach(question => {
        question.addEventListener('click', function() {
            this.parentNode.classList.toggle('active');
            
            faqQuestions.forEach(otherQuestion => {
                if (otherQuestion !== question) {
                    otherQuestion.parentNode.classList.remove('active');
                }
            });
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.querySelector('.custom-gallery-carousel');
    const prevBtn = document.querySelector('.custom-carousel-control.prev');
    const nextBtn = document.querySelector('.custom-carousel-control.next');
    const items = document.querySelectorAll('.gallery-item-card');
    
    const itemWidth = items[0].offsetWidth + 20; 
    
    prevBtn.addEventListener('click', () => {
        carousel.scrollBy({ left: -itemWidth, behavior: 'smooth' });
    });
    
    nextBtn.addEventListener('click', () => {
        carousel.scrollBy({ left: itemWidth, behavior: 'smooth' });
    });
});