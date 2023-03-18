var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Express' });
});

router.get('/api/get/back', function(req, res){
	res.status(200).json({
    	"message" : "hello get api back"
        });
 });

router.post('/api/post/back',function(req, res){
	res.status(200).json({
    	"message" : "hello post api back"
    });    
}); 

module.exports = router;
