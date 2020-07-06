;(function ($) {
    $.fn.fixHeader = function () {
        return this.each(function () {
            var $table = $(this);
            var $sp = $table.parent();
            var tableOffset = $table.position().top;
            var $tableFixed = $("<table />")
                .prop('class', $table.prop('class'))
                .css({ position: "fixed", "table-layout": "fixed", display: "none", "margin-top": "0px" });
            $table.before($tableFixed);
            $tableFixed.append($table.find("thead").clone());

            $sp.bind("scroll", function () {
                var offset = $(this).scrollTop();

                if (offset > tableOffset && $tableFixed.is(":hidden")) {
                    $tableFixed.show();
                    var p = $table.position();
                    var offset = $sp.offset();

                    //Set the left and width to match the source table and the top to match the scroll parent
                    $tableFixed.css({ top: (offset ? offset.top : 0) + "px", "background":"#ddd","font-size": "1.1vw","left":$table.offset().left + "px"}).width($table.width());

                    //Set the width of each column to match the source table
                    $.each($table.find('th, td'), function (i, th) {
                        $($tableFixed.find('th, td')[i]).width($(th).width());
                    });

                }
                else if (offset <= tableOffset && !$tableFixed.is(":hidden")) {
                    $tableFixed.hide();
                }
            });
        });
    };
})(jQuery);