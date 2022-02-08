(function ($) {
    // USE STRICT
    "use strict";
    $.fn.counters = function(options) {
        return this.each(function() {
            var container = $(this),
                elements = container.find('.count_to .odometer');
            //trigger displaying of thumbnails
            container.appear(function() {
                elements.each(function(i) {
                    var $count = $(this);
                    var od = new Odometer({
                        el: $count[0],
                        format: '',
                        theme: 'minimal',
                        duration: $count.data('duration')
                    });
                    od.update($count.data('number'));
                });
            });
        });
    };
    $.fn.animate_on_appear = function(options_passed){
        return this.each(function(){
            var self = $(this);
            self.appear( function(){
                var effect = $(this).data('animation');
                var delay = $(this).data('delay');
                $(this).delay(delay).queue( function() {
                $(this).removeClass('with_animation').addClass( effect );
               });
            });
        });
    };
    $.fn.chart_skill = function(options){
        return this.each(function(){
            var container = $(this), elements = container.find('.chart');
            //trigger displaying of thumbnails
            container.appear(function(){
                elements.each(function(i){
                    var $chart = $(this);
                    var color = $(this).data('color');
                    var color2 = $(this).data('color2');
                        $chart.easyPieChart({
                            lineWidth: 8,
                            size: 140,
                            trackColor: color2,
                            scaleColor: false,
                            barColor: color,
                            barColor2: color,
                            animate:2000
                        });
                });
            });
        });
    }
    /* ----------------------------- Fullscreen Section ---------------------- */

})(jQuery);


$(document).ready(function () {
    if($.fn.chart_skill)
    {
        $('.chart_skill').chart_skill();
    }
    if($.fn.counters)
    {
        $('.state-col-inner').counters();
    }

//   skill chart js
    $('.chart_skill > .chart > span').bind("DOMSubtreeModified",function(ev){
        ev.target.parentNode.setAttribute('data-percent', ev.target.innerText);
    });

// variables
    var $header_top = $('graph_header');


    // fullpage customization
    $('#fullpage').fullpage({
      sectionSelector: '.vertical-scrolling',
      slideSelector: '.horizontal-scrolling',
      navigation: true,
      slidesNavigation: true,
      controlArrows: true,
      responsiveWidth: 900,

      afterLoad: function(anchorLink, index) {
        $header_top.css('background', 'rgba(0, 47, 77, .3)');
        if (index == 5) {
            $('#fp-nav').hide();
          }
      },

      onLeave: function(index, nextIndex, direction) {
        if(index == 5) {
          $('#fp-nav').show();
        }
      },

      afterSlideLoad: function( anchorLink, index, slideAnchor, slideIndex) {
        if(anchorLink == 'fifthSection' && slideIndex == 1) {
          $.fn.fullpage.setAllowScrolling(false, 'up');
          $header_top.css('background', 'transparent');
          $(this).css('background', '#374140');
          $(this).find('h2').css('color', 'white');
          $(this).find('h3').css('color', 'white');
          $(this).find('p').css(
            {
              'color': '#DC3522',
              'opacity': 1,
              'transform': 'translateY(0)'
            }
          );
        }
      },

      onSlideLeave: function( anchorLink, index, slideIndex, direction) {
        if(anchorLink == 'fifthSection' && slideIndex == 1) {
          $.fn.fullpage.setAllowScrolling(true, 'up');
          $header_top.css('background', 'rgba(0, 47, 77, .3)');
        }
      }
    });
});
