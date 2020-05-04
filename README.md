# SomeBody 
NAVER AI_Burning_Day 2020 **본선 진출작** 
- 네이버 클라우드 플랫폼 API를 활용한 앱 또는 웹 개발  

## Team : 아주아주공주
🙎‍♀️ [김우정](https://github.com/woodongk) - 기획   
👸🏻 [박태훈](https://github.com/Hoonhooney) - 프론트엔드   
🙎‍♀️ [김희아](https://github.com/eminem54) - 백엔드   

## Introduction
### 누구나의 그 어떠한 몸짓도 음악이 된다!
사용자의 몸 동작을 **Pose Estimation API**를 이용해 좌표로 환산하여 음악으로 만들어주는 서비스 

<h1 align="center"><img src="https://github.com/woodongk/Somebody/blob/master/imgs/summary.png"></h1>
    
### Description
**구현 기능 1. 음악 생성**  
- 사전에 신체 부위 별로 음악 할당  
	-	Beat  
		   - 0 : 머리 - crash  
		   - 1 : 배 - hat  
		   - 3 : 오른팔꿈치 - tom  
		   - 4 : 오른팔 - kick  
		   - 6 : 왼쪽팔꿈치 - snare  
		   - 7 : 왼팔 - bongo  
		   - 9 : 오른쪽무릎 - clap  
		   - 10 : 오른발 - cow bell  
		   - 12 : 왼쪽무릎 - maracas  
		   - 13 : 왼쪽발 - rid  
   - Melody 
	   - 블루스 스케일 
	   (도 - 미 플랫 - 파 - 파 샾 - 솔 - 시 플랫 - 도)  
     
- 몸의 좌표 값이 가장 많이 변화한 신체 부위에 할당된 Beat와 전체 좌표 값 평균과 비교한 한 프레임의  평균 값에 의해 결정되는 Melody를 합성하여 새로운 음원 생성  
   - [Beat + Beat] + [Melody] = 새로운 음악  
- 생성된 음원과 원래의 비디오가 합쳐져 새로운 뮤직비디오로 재탄생    
- 업로드한 비디오에서 원래 있던 오디오를 삭제. 무성의 비디오로 추출  
- 생성된 음원과 앞서 음원을 추출한 무성의 비디오가 합쳐져 새로운 뮤직비디오로 재탄생  
  
**구현 기능 2. 사운드 로그 생성**  
- 사용자의 몸짓 변화량이 활발한 (크게 변화한) 부위를 셈하여 분석 제공  
   - 변화량이 활발할 것 같은 5개의 신체부위에 대한 analysis summary  
- 사용자의 몸짓 변화량의 총량에 따른 분류  


### 일정  
- 예선 일정 : 2020/1/21~2020/1/31       
- 본선 일정 : 2020/2/13~2020/2/15
  
 