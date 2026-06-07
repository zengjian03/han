<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="icon" href="./images/logo.png">
  <title>警告</title>
  <script src="./js/rem.js"></script>
  <script>
    window.onload = function() {
      var pcPageEl = document.getElementsByClassName('container')[0]
      var mPageEl = document.getElementsByClassName('m-container')[0]
      if(/Android|webOS|iPhone|iPod|BlackBerry/i.test(navigator.userAgent)) {
        pcPageEl.style.display = 'none'
        mPageEl.style.display = 'block'
      } else {
        pcPageEl.style.display = 'block'
        mPageEl.style.display = 'none'
      }
    }
  </script>
  <style>
    *{
      margin: 0;
      padding: 0;
    }
    /* body{
      position: absolute;
      left: 50%;
      width: 90%;
      transform: translateX(-50%);
    } */
    .container{
      width: 100%;
      height: 100%;
      display: none;
    }
    .header{
      width: 100%;
      height: 23.125rem /* 370/16 */;
      background:-moz-linear-gradient(270deg, #FF4900 0%, #EC0600 100%);  
		  background:-webkit-linear-gradient(270deg, #FF4900 0%, #EC0600 100%);   
		  background: -o-linear-gradient(270deg, #FF4900 0%, #EC0600 100%); 
		  background: -ms-linear-gradient(270deg, #FF4900 0%, #EC0600 100%); 
		  background: linear-gradient(270deg, #FF4900 0%, #EC0600 100%);
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .logo{
      position: absolute;
      top: 2.3125rem /* 37/16 */;
      left: 2.75rem /* 44/16 */;
      
    }
    .logo img{
      width: 3.4375rem /* 55/16 */;
      height: 3.375rem /* 54/16 */;
      vertical-align: middle;
    }
    .logo span{
      font-size: 1.875rem /* 30/16 */;
      color: #fff;
      vertical-align: middle;
    }
    .title{
      text-align: center;
    }
    .title img{
      vertical-align: middle;
    }
    .title span{
      font-size: 3rem /* 48/16 */;
      color: #fff;
      vertical-align: middle;
    }
    .content{
      width: 100%;
      height: calc(100vh - 23.125rem);/* 370/16 */
      display: flex;
      justify-content: center;
      align-items: center;
      background-color: #fff;
    }
    .telephone {
      position: absolute;
      right: 1.875rem /* 30/16 */;
      top: 2.5rem /* 40/16 */;
      font-size: 1.125rem /* 18/16 */;
      color: #fff;
    }
    .left{
      margin-right: 6.25rem /* 100/16 */;
    }
    .left > div{
      margin-bottom: 1.875rem /* 30/16 */;
    }
    .left > div:last-child{
      margin-bottom: 0px;
    }
    .left span{
      width: 270px;
      display: inline-block;
      font-size: 26px;
      color: #000000;
      font-weight: bold;
      text-align: right;
      
    }
    .left a{
      margin-left: 1.875rem /* 30/16 */;
      font-size: 1.9rem /* 24/16 */;
      color: #1D419D;
    }
    .right{
      display: flex;
      /* flex-direction: column; */
      justify-content: center;
      align-items: center;
    }
    .right .title {
      display: flex;
    }
    .right p{
      font-size: 2rem /* 32/16 */;
      color: #000000;
      text-align: center;
      margin: 0 2.2rem;
    }
    .right img{
      width: 16rem /* 256/16 */;
      height: 15.625rem /* 250/16 */;
      margin: 1.25rem 2rem 0;
    }
    .right .img1 {
      margin-left: 5rem;
      margin-right: 4.1rem;
    }

    
    .m-container{
      width: 100%;
      height: 100%;
      display: none;
    }
    .m-header{
      width: 100%;
      height: 25rem /* 400/16 */;
      background:-moz-linear-gradient(270deg, #FF4900 0%, #EC0600 100%);  
		  background:-webkit-linear-gradient(270deg, #FF4900 0%, #EC0600 100%);   
		  background: -o-linear-gradient(270deg, #FF4900 0%, #EC0600 100%); 
		  background: -ms-linear-gradient(270deg, #FF4900 0%, #EC0600 100%); 
		  background: linear-gradient(270deg, #FF4900 0%, #EC0600 100%);
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
    .m-logo{
 
    }
    .m-logo img{
      width: 2.5rem /* 40/16 */;
      height: 2.5rem /* 40/16 */;
      vertical-align: middle;
    }
    .m-logo span{
      font-size: 2.625rem /* 42/16 */;
      color: #fff;
      vertical-align: middle;
    }
    .m-title{
      margin-top: 2.5rem /* 40/16 */;
      text-align: center;
    }
    .m-title img{
      width: 6.25rem /* 100/16 */;
      height: 6.25rem /* 100/16 */;
      vertical-align: middle;
    }
    .m-title span{
      font-size: 3rem /* 48/16 */;
      color: #fff;
      vertical-align: middle;
    }
    .m-content{
      display: flex;
      flex-direction: column;
      align-items: center;

    }
    .m-code{
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .m-code > div{
      margin-top: 3.125rem /* 50/16 */;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .m-code > div > p{
      font-size: 1.875rem /* 30/16 */;
      font-weight: bold;
    }
    .m-code > img{
      margin-top: 1.25rem /* 20/16 */;
      width: 15.625rem /* 250/16 */;
      height: 15.625rem /* 250/16 */;
    }

    .url{
      margin-top: 3.75rem /* 60/16 */;
    }
    .url > div{
      margin-bottom: 1.25rem /* 20/16 */;
      display: flex;
      flex-direction: column;
      align-items: center;
      font-size: 1.5rem /* 24/16 */;
    }
    .url > div > p{
      font-weight: bold;
      
    }

    .m-telephone {
      position: absolute;
      right: .3125rem /* 5/16 */;
      bottom: 1.875rem /* 30/16 */;
      font-size: .875rem /* 14/16 */;
      color: #fff;
      transform:scale(0.9);
    }
    .bottom {
      position: absolute;
      left: 50%;
      bottom: .9375rem /* 15/16 */;
      margin-left: -72px;
    }
    .bottom a {
        font-size: 12px;
        cursor: pointer;
        text-decoration: none;
        color: #000000;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="logo">
        <img src="./images/logo.png" alt="">
        <span>上海市反电信网络诈骗中心提醒您</span>
      </div>
      <div class="title">
        <img src="./images/alarm.svg" alt="">
        <span>该网站疑似诈骗网站</span>
      </div>
    </div>
    <div class="content">
      <!-- <div class="left">
		    <div><span>投资理财诈骗防范宣传</span><a href="https://weibo.com/5969745163?tabtype=newVideo&layerid=5213993595830721">https://weibo.com/5969745163?tabtype=newVideo&layerid=5213993595830721</a></div>
		    <div><span>冒充客服诈骗防范宣传</span><a href="https://weibo.com/5969745163?tabtype=newVideo&layerid=5179917251644492">https://weibo.com/5969745163?tabtype=newVideo&layerid=5179917251644492</a></div>
		    <div><span>虚假购物诈骗防范宣传</span><a href="https://weibo.com/5969745163?tabtype=newVideo&layerid=5212544014224251">https://weibo.com/5969745163?tabtype=newVideo&layerid=5212544014224251</a></div>
        <div><span>兼职刷单诈骗防范宣传</span><a href="https://weibo.com/5969745163?tabtype=newVideo&layerid=5223053265209100">https://weibo.com/5969745163?tabtype=newVideo&layerid=5223053265209100</a></div>
        <div><span>假冒公检法诈骗防范宣传</span><a href="https://weibo.com/5969745163?tabtype=newVideo&layerid=5216168132217467">https://weibo.com/5969745163?tabtype=newVideo&layerid=5216168132217467</a></div>
		    <div><span>涉黄引流诈骗防范宣传</span><a href="https://weibo.com/5969745163?tabtype=newVideo&layerid=5204625380611673">https://weibo.com/5969745163?tabtype=newVideo&layerid=5204625380611673</a></div>
      </div> -->
      <div class="left">
		    <div><a href="https://shfzxc.cn/video/tzlczp.mp4">投资理财诈骗防范宣传</a></div>
		    <div><a href="https://shfzxc.cn/video//mckfzp.mp4">冒充客服诈骗防范宣传</a></div>
		    <div><a href="https://shfzxc.cn/video/wgzp.mp4">虚假购物诈骗防范宣传</a></div>
        <div><a href="https://shfzxc.cn/video/jzsdzp.mp4">兼职刷单诈骗防范宣传</a></div>
        <div><a href="https://shfzxc.cn/video/jmgjfzp.mp4">假冒公检法诈骗防范宣传</a></div>
		    <div><a href="https://shfzxc.cn/video/shylzp.mp4">涉黄引流诈骗防范宣传</a></div>
      </div>
      <div class="right">
        <div>
          <div class="title">
            <p>“803反诈”智能体APP</p>
            <p>国家反诈中心APP</p>
            <p>“金护”APP</p>
          </div>
          <p>（扫码或到各大官方应用商店下载）</p>
          <img class="img1" src="https://shfzxc.cn/video/803.png" alt="">
          <img src="https://shfzxc.cn/video/code.png" alt="">
          <img src="https://shfzxc.cn/video/jh.png" alt="">
        </div>
      </div>
    </div>
    <p class="telephone">咨询申诉电话：021-96110</p>
	  <div class="bottom"><a href="https://beian.miit.gov.cn">沪ICP备18029816号-2</a></div>
  </div>

  <div class="m-container">
    <div class="m-header">
      <div class="m-logo">
        <img src="./images/logo.png" alt="">
        <span>上海市反电信网络诈骗中心提醒您</span>
      </div>
      <div class="m-title">
        <img src="./images/alarm.svg" alt="">
        <span>该网站疑似诈骗网站</span>
      </div>
      <p class="m-telephone">咨询申诉电话：021-96110</p>
    </div>
    <div class="m-content">
      <div class="url">
        <div><span>投资理财诈骗防范宣传</span><a href="https://weibo.com/5969745163?tabtype=newVideo&layerid=5213993595830721">https://weibo.com/5969745163?tabtype=newVideo&layerid=5213993595830721</a></div>
		    <div><span>冒充客服诈骗防范宣传</span><a href="https://weibo.com/5969745163?tabtype=newVideo&layerid=5179917251644492">https://weibo.com/5969745163?tabtype=newVideo&layerid=5179917251644492</a></div>
		    <div><span>虚假购物诈骗防范宣传</span><a href="https://weibo.com/5969745163?tabtype=newVideo&layerid=5212544014224251">https://weibo.com/5969745163?tabtype=newVideo&layerid=5212544014224251</a></div>
        <div><span>兼职刷单诈骗防范宣传</span><a href="https://weibo.com/5969745163?tabtype=newVideo&layerid=5223053265209100">https://weibo.com/5969745163?tabtype=newVideo&layerid=5223053265209100</a></div>
        <div><span>假冒公检法诈骗防范宣传</span><a href="https://weibo.com/5969745163?tabtype=newVideo&layerid=5216168132217467">https://weibo.com/5969745163?tabtype=newVideo&layerid=5216168132217467</a></div>
		    <div><span>涉黄引流诈骗防范宣传</span><a href="https://weibo.com/5969745163?tabtype=newVideo&layerid=5204625380611673">https://weibo.com/5969745163?tabtype=newVideo&layerid=5204625380611673</a></div>
      </div>
      <div class="m-code">
        <div>
          <p>国家反诈中心APP</p>
          <p>（扫码或到各大官方应用商店下载）</p>
        </div>
        <img src="./images/code.png" alt="">
      </div>
    </div>
    <div class="bottom"><a href="https://beian.miit.gov.cn">沪ICP备18029816号-2</a></div>
  </div>
</body>
</html>