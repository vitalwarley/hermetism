// Populate the sidebar
//
// This is a script, and not included directly in the page, to control the total size of the book.
// The TOC contains an entry for each page, so if each page includes a copy of the TOC,
// the total size of the page becomes O(n**2).
class MDBookSidebarScrollbox extends HTMLElement {
    constructor() {
        super();
    }
    connectedCallback() {
        this.innerHTML = '<ol class="chapter"><li class="chapter-item expanded affix "><a href="index.html">Introduction</a></li><li class="chapter-item expanded affix "><li class="part-title">Astrology</li><li class="chapter-item expanded "><div><strong aria-hidden="true">1.</strong> Signs</div></li><li><ol class="section"><li class="chapter-item expanded "><a href="astrology/raw/sagittarius.html"><strong aria-hidden="true">1.1.</strong> Sagittarius</a></li><li class="chapter-item expanded "><a href="astrology/raw/capricorn.html"><strong aria-hidden="true">1.2.</strong> Capricorn</a></li><li class="chapter-item expanded "><a href="astrology/raw/aquarius.html"><strong aria-hidden="true">1.3.</strong> Aquarius</a></li><li class="chapter-item expanded "><a href="astrology/raw/pisces.html"><strong aria-hidden="true">1.4.</strong> Pisces</a></li></ol></li><li class="chapter-item expanded "><div><strong aria-hidden="true">2.</strong> Planets</div></li><li><ol class="section"><li class="chapter-item expanded "><a href="raw/planets/sun.html"><strong aria-hidden="true">2.1.</strong> Sun</a></li><li class="chapter-item expanded "><a href="raw/planets/moon.html"><strong aria-hidden="true">2.2.</strong> Moon</a></li></ol></li><li class="chapter-item expanded "><li class="part-title">Tarot</li><li class="chapter-item expanded "><div><strong aria-hidden="true">3.</strong> Sign Correspondences</div></li><li><ol class="section"><li class="chapter-item expanded "><div><strong aria-hidden="true">3.1.</strong> Sagittarius</div></li><li><ol class="section"><li class="chapter-item expanded "><a href="tarot/saggitarius/eight_of_wands.html"><strong aria-hidden="true">3.1.1.</strong> Eight of Wands</a></li><li class="chapter-item expanded "><a href="tarot/saggitarius/nine_of_wands.html"><strong aria-hidden="true">3.1.2.</strong> Nine of Wands</a></li><li class="chapter-item expanded "><a href="tarot/saggitarius/ten_of_wands.html"><strong aria-hidden="true">3.1.3.</strong> Ten of Wands</a></li><li class="chapter-item expanded "><a href="tarot/saggitarius/king_of_wands.html"><strong aria-hidden="true">3.1.4.</strong> King of Wands</a></li></ol></li><li class="chapter-item expanded "><div><strong aria-hidden="true">3.2.</strong> Capricorn</div></li><li><ol class="section"><li class="chapter-item expanded "><a href="tarot/capricorn/queen_of_pentacles.html"><strong aria-hidden="true">3.2.1.</strong> Queen of Pentacles</a></li><li class="chapter-item expanded "><a href="tarot/capricorn/two_of_pentacles.html"><strong aria-hidden="true">3.2.2.</strong> Two of Pentacles</a></li><li class="chapter-item expanded "><a href="tarot/capricorn/three_of_pentacles.html"><strong aria-hidden="true">3.2.3.</strong> Three of Pentacles</a></li><li class="chapter-item expanded "><a href="tarot/capricorn/four_of_pentacles.html"><strong aria-hidden="true">3.2.4.</strong> Four of Pentacles</a></li></ol></li><li class="chapter-item expanded "><div><strong aria-hidden="true">3.3.</strong> Aquarius</div></li><li><ol class="section"><li class="chapter-item expanded "><a href="tarot/aquarius/five_of_swords.html"><strong aria-hidden="true">3.3.1.</strong> Five of Swords</a></li><li class="chapter-item expanded "><a href="tarot/aquarius/six_of_swords.html"><strong aria-hidden="true">3.3.2.</strong> Six of Swords</a></li><li class="chapter-item expanded "><a href="tarot/aquarius/seven_of_swords.html"><strong aria-hidden="true">3.3.3.</strong> Seven of Swords</a></li><li class="chapter-item expanded "><a href="tarot/aquarius/eight_of_swords.html"><strong aria-hidden="true">3.3.4.</strong> Eight of Swords</a></li></ol></li><li class="chapter-item expanded "><div><strong aria-hidden="true">3.4.</strong> Pisces</div></li><li><ol class="section"><li class="chapter-item expanded "><a href="tarot/pisces/eight_cups.html"><strong aria-hidden="true">3.4.1.</strong> Eight of Cups</a></li><li class="chapter-item expanded "><a href="tarot/pisces/nine_cups.html"><strong aria-hidden="true">3.4.2.</strong> Nine of Cups</a></li><li class="chapter-item expanded "><a href="tarot/pisces/ten_cups.html"><strong aria-hidden="true">3.4.3.</strong> Ten of Cups</a></li><li class="chapter-item expanded "><a href="tarot/pisces/king_cups.html"><strong aria-hidden="true">3.4.4.</strong> King of Cups</a></li><li class="chapter-item expanded "><a href="tarot/pisces/the_moon.html"><strong aria-hidden="true">3.4.5.</strong> The Moon</a></li></ol></li></ol></li><li class="chapter-item expanded "><li class="part-title">Angels</li><li class="chapter-item expanded "><div><strong aria-hidden="true">4.</strong> Sagittarius Angels</div></li><li><ol class="section"><li class="chapter-item expanded "><a href="angels/sagittarius/daniel.html"><strong aria-hidden="true">4.1.</strong> Daniel</a></li><li class="chapter-item expanded "><a href="angels/sagittarius/nanael.html"><strong aria-hidden="true">4.2.</strong> Nanael</a></li><li class="chapter-item expanded "><a href="angels/sagittarius/nithael.html"><strong aria-hidden="true">4.3.</strong> Nithael</a></li><li class="chapter-item expanded "><a href="angels/sagittarius/vehuel.html"><strong aria-hidden="true">4.4.</strong> Vehuel</a></li><li class="chapter-item expanded "><a href="angels/sagittarius/imamiah.html"><strong aria-hidden="true">4.5.</strong> Imamiah</a></li><li class="chapter-item expanded "><a href="angels/sagittarius/hahasiah.html"><strong aria-hidden="true">4.6.</strong> Hahasiah</a></li></ol></li><li class="chapter-item expanded "><div><strong aria-hidden="true">5.</strong> Capricorn Angels</div></li><li><ol class="section"><li class="chapter-item expanded "><a href="angels/capricorn/mebahiah.html"><strong aria-hidden="true">5.1.</strong> Mebahiah</a></li><li class="chapter-item expanded "><a href="angels/capricorn/poyel.html"><strong aria-hidden="true">5.2.</strong> Poyel</a></li><li class="chapter-item expanded "><a href="angels/capricorn/nemamiah.html"><strong aria-hidden="true">5.3.</strong> Nemamiah</a></li><li class="chapter-item expanded "><a href="angels/capricorn/ieialel.html"><strong aria-hidden="true">5.4.</strong> Ieialel</a></li><li class="chapter-item expanded "><a href="angels/capricorn/harahel.html"><strong aria-hidden="true">5.5.</strong> Harahel</a></li><li class="chapter-item expanded "><a href="angels/capricorn/mitzrael.html"><strong aria-hidden="true">5.6.</strong> Mitzrael</a></li></ol></li><li class="chapter-item expanded "><div><strong aria-hidden="true">6.</strong> Aquarius Angels</div></li><li><ol class="section"><li class="chapter-item expanded "><a href="angels/aquarius/anauel.html"><strong aria-hidden="true">6.1.</strong> Anauel</a></li><li class="chapter-item expanded "><a href="angels/aquarius/damabiah.html"><strong aria-hidden="true">6.2.</strong> Damabiah</a></li><li class="chapter-item expanded "><a href="angels/aquarius/iahhel.html"><strong aria-hidden="true">6.3.</strong> Iahhel</a></li><li class="chapter-item expanded "><a href="angels/aquarius/manakel.html"><strong aria-hidden="true">6.4.</strong> Manakel</a></li><li class="chapter-item expanded "><a href="angels/aquarius/mehiel.html"><strong aria-hidden="true">6.5.</strong> Mehiel</a></li><li class="chapter-item expanded "><a href="angels/aquarius/umabel.html"><strong aria-hidden="true">6.6.</strong> Umabel</a></li></ol></li><li class="chapter-item expanded "><div><strong aria-hidden="true">7.</strong> Pisces</div></li><li><ol class="section"><li class="chapter-item expanded "><a href="angels/pisces/eyael.html"><strong aria-hidden="true">7.1.</strong> Eyael</a></li><li class="chapter-item expanded "><a href="angels/pisces/habuhiah.html"><strong aria-hidden="true">7.2.</strong> Habuhiah</a></li><li class="chapter-item expanded "><a href="angels/pisces/haiaiel.html"><strong aria-hidden="true">7.3.</strong> Haiaiel</a></li><li class="chapter-item expanded "><a href="angels/pisces/mumiah.html"><strong aria-hidden="true">7.4.</strong> Mumiah</a></li><li class="chapter-item expanded "><a href="angels/pisces/rochel.html"><strong aria-hidden="true">7.5.</strong> Rochel</a></li><li class="chapter-item expanded "><a href="angels/pisces/yabamiah.html"><strong aria-hidden="true">7.6.</strong> Yabamiah</a></li></ol></li><li class="chapter-item expanded "><li class="part-title">Synthesis</li><li class="chapter-item expanded "><div><strong aria-hidden="true">8.</strong> Signs</div></li><li><ol class="section"><li class="chapter-item expanded "><a href="astrology/synthesis/aries.html"><strong aria-hidden="true">8.1.</strong> Aries</a></li><li class="chapter-item expanded "><a href="astrology/synthesis/libra.html"><strong aria-hidden="true">8.2.</strong> Libra</a></li><li class="chapter-item expanded "><a href="astrology/synthesis/scorpio.html"><strong aria-hidden="true">8.3.</strong> Scorpio</a></li><li class="chapter-item expanded "><a href="astrology/synthesis/sagittarius.html"><strong aria-hidden="true">8.4.</strong> Sagittarius</a></li><li class="chapter-item expanded "><a href="astrology/synthesis/capricorn.html"><strong aria-hidden="true">8.5.</strong> Capricorn</a></li><li class="chapter-item expanded "><a href="astrology/synthesis/aquarius.html"><strong aria-hidden="true">8.6.</strong> Aquarius</a></li><li class="chapter-item expanded "><a href="astrology/synthesis/pisces.html"><strong aria-hidden="true">8.7.</strong> Pisces</a></li></ol></li><li class="chapter-item expanded "><div><strong aria-hidden="true">9.</strong> Planets</div></li><li><ol class="section"><li class="chapter-item expanded "><a href="synthesis/planets/sun.html"><strong aria-hidden="true">9.1.</strong> Sun</a></li><li class="chapter-item expanded "><a href="synthesis/planets/moon.html"><strong aria-hidden="true">9.2.</strong> Moon</a></li></ol></li></ol>';
        // Set the current, active page, and reveal it if it's hidden
        let current_page = document.location.href.toString().split("#")[0];
        if (current_page.endsWith("/")) {
            current_page += "index.html";
        }
        var links = Array.prototype.slice.call(this.querySelectorAll("a"));
        var l = links.length;
        for (var i = 0; i < l; ++i) {
            var link = links[i];
            var href = link.getAttribute("href");
            if (href && !href.startsWith("#") && !/^(?:[a-z+]+:)?\/\//.test(href)) {
                link.href = path_to_root + href;
            }
            // The "index" page is supposed to alias the first chapter in the book.
            if (link.href === current_page || (i === 0 && path_to_root === "" && current_page.endsWith("/index.html"))) {
                link.classList.add("active");
                var parent = link.parentElement;
                if (parent && parent.classList.contains("chapter-item")) {
                    parent.classList.add("expanded");
                }
                while (parent) {
                    if (parent.tagName === "LI" && parent.previousElementSibling) {
                        if (parent.previousElementSibling.classList.contains("chapter-item")) {
                            parent.previousElementSibling.classList.add("expanded");
                        }
                    }
                    parent = parent.parentElement;
                }
            }
        }
        // Track and set sidebar scroll position
        this.addEventListener('click', function(e) {
            if (e.target.tagName === 'A') {
                sessionStorage.setItem('sidebar-scroll', this.scrollTop);
            }
        }, { passive: true });
        var sidebarScrollTop = sessionStorage.getItem('sidebar-scroll');
        sessionStorage.removeItem('sidebar-scroll');
        if (sidebarScrollTop) {
            // preserve sidebar scroll position when navigating via links within sidebar
            this.scrollTop = sidebarScrollTop;
        } else {
            // scroll sidebar to current active section when navigating via "next/previous chapter" buttons
            var activeSection = document.querySelector('#sidebar .active');
            if (activeSection) {
                activeSection.scrollIntoView({ block: 'center' });
            }
        }
        // Toggle buttons
        var sidebarAnchorToggles = document.querySelectorAll('#sidebar a.toggle');
        function toggleSection(ev) {
            ev.currentTarget.parentElement.classList.toggle('expanded');
        }
        Array.from(sidebarAnchorToggles).forEach(function (el) {
            el.addEventListener('click', toggleSection);
        });
    }
}
window.customElements.define("mdbook-sidebar-scrollbox", MDBookSidebarScrollbox);
