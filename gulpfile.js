const gulp = require('gulp');
const concat = require('gulp-concat');
const cssnano = require('gulp-cssnano');
const uglify = require('gulp-uglify');
const sass = require('gulp-sass');
const rename = require('gulp-rename');
const autoprefixer = require('gulp-autoprefixer');
const gulpLog = require('gutil');

const AUTOPREFIXER_BROWSERS = [
  'ie >= 10',
  'ie_mob >= 10',
  'ff >= 30',
  'chrome >= 34',
  'safari >= 7',
  'opera >= 23',
  'ios >= 7',
  'android >= 4.4',
  'bb >= 10'
];

gulp.task('sass' , function() {
  gulpLog.log("\nStarting task Sass........");
  return gulp.src('static/scss/**/*.scss')
    .pipe(sass({
      outputStyle: 'nested',
      precision: 10,
      includePaths: ['.'],
      onError: console.error.bind(console, 'Sass error:')
    }))
    .pipe(concat('styles.css'))
    .pipe(autoprefixer({browsers: AUTOPREFIXER_BROWSERS}))
    .pipe(cssnano())
    .pipe(rename({
      basename: "styles",
      suffix: ".min",
      extname: ".css"
    }))
    .pipe(gulp.dest('static/css'))
});

gulp.task('scripts', function(){
  gulpLog.log("\nStarting task Scripts........");
  return gulp.src('static/js/jquery/**/*.js')
  .pipe(uglify())
  .pipe(rename({
    basename: 'app',
    suffix: '.min',
    extname: '.js'
  }))
  .pipe(gulp.dest('static/js'))
});

gulp.task('watch', function(){
  gulp.watch('static/scss/**/*.scss', gulp.series('sass'));
  gulp.watch('static/js/jquery/**/*.js', gulp.series('scripts'));
});