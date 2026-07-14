import streamlit as st
import streamlit.components.v1 as components
import random

# --- Streamlit 페이지 설정 ---
st.set_page_config(
    page_title="감도 여행 다트 클론 | 나만의 랜덤 여행",
    page_icon="🎯",
    layout="wide",
)

# --- 상단 타이틀 ---
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; font-size: 3rem;">🎯 감도 여행 다트 [클론]</h1>
        <p style="color: #aaa; font-size: 1.2rem;">힘과 방향을 조절해서 다트를 던지세요! 꽂힌 곳이 당신의 여행지입니다.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- 메인 게임 엔진 (HTML/JS/CSS) ---
# kimgamdo.com의 느낌을 내기 위해 SVG 지도와 JS 물리 엔진을 사용합니다.
# 이 영역 전체가 사용자 정의 HTML 컴포넌트로 실행됩니다.

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Streamlit Dart Game</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #1a1a1a;
            color: white;
            font-family: 'Arial', sans-serif;
            overflow: hidden; /* 스크롤 방지 */
            display: flex;
            justify-content: center;
            align-items: center;
            height: 90vh;
        }

        #game-container {
            position: relative;
            width: 700px;
            height: 800px;
            background-color: #262626;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            overflow: hidden;
            border: 2px solid #333;
        }

        /* 심플한 한국 지도 SVG (색 구분) */
        #map-bg {
            position: absolute;
            top: 50px;
            left: 50px;
            width: 600px;
            height: 700px;
            /* 주의: 아래 SVG 소스는 예시입니다. 실제 배포시는 더 정확한 SVG로 교체 가능합니다. */
            background-image: url('data:image/svg+xml;charset=utf-8,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 710"%3E%3Cpath d="M298 625l-10-8-12 1-7-10 1-13 14-11 20 2 13-3 12 10 7 19-8 15-20 8z" fill="%23FFCDD2" stroke="%23333" stroke-width="2"/%3E%3Cpath d="M200 480l-15-25 5-20 20-5 30 10 10 25-10 20-25 5z" fill="%23C8E6C9" stroke="%23333" stroke-width="2"/%3E%3Cpath d="M120 300l10-30 40-10 30 20-5 35-40 20z" fill="%23BBDEFB" stroke="%23333" stroke-width="2"/%3E%3Cpath d="M350 200l20-40 50 10 15 45-25 30-45 5z" fill="%23FFF9C4" stroke="%23333" stroke-width="2"/%3E%3Cpath d="M420 500l-5-40 30-20 40 10 5 45-30 30z" fill="%23E1BEE7" stroke="%23333" stroke-width="2"/%3E%3C/svg%3E');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            opacity: 0.8;
            pointer-events: none; /* 지도는 클릭 방지 */
        }

        /* 다트 핀 */
        #dart {
            position: absolute;
            width: 20px;
            height: 60px;
            background-color: #ff3b30; /* 빨간색 다트 */
            border-radius: 10px 10px 2px 2px;
            transform: translate(-50%, -100%); /* 핀 끝이 좌표에 오도록 */
            display: none; /* 처음엔 숨김 */
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
            z-index: 10;
        }
        #dart::after { /* 다트 깃털 */
            content: '';
            position: absolute;
            top: -15px;
            left: -10px;
            width: 40px;
            height: 25px;
            background-color: #ff6b62;
            clip-path: polygon(50% 0%, 100% 100%, 0% 100%);
            border-radius: 5px;
        }

        /* 드래그 시 표시되는 조준선 */
        #aim-line {
            position: absolute;
            background-color: rgba(255, 255, 255, 0.5);
            height: 4px;
            border-radius: 2px;
            transform-origin: left center;
            display: none;
            pointer-events: none;
            z-index: 5;
        }

        /* 꽂힐 때 이펙트 (충격파) */
        .impact-effect {
            position: absolute;
            border: 4px solid #ff3b30;
            border-radius: 50%;
            pointer-events: none;
            opacity: 0;
            animation: impact-anim 0.6s ease-out;
            z-index: 11;
        }

        @keyframes impact-anim {
            0% { width: 0; height: 0; opacity: 1; transform: translate(-50%, -50%); }
            100% { width: 100px; height: 100px; opacity: 0; transform: translate(-50%, -50%); }
        }

        /* 결과 표시창 */
        #result-display {
            position: absolute;
            top: 20px;
            left: 20px;
            padding: 10px 20px;
            background-color: rgba(0, 0, 0, 0.7);
            border-radius: 10px;
            font-size: 1.1rem;
            display: none;
            z-index: 20;
        }
    </style>
</head>
<body>
    <div id="game-container">
        <div id="map-bg"></div>
        <div id="aim-line"></div>
        <div id="dart"></div>
        <div id="result-display">📍 당첨된 여행지: ...</div>
    </div>

    <script>
        const container = document.getElementById('game-container');
        const dart = document.getElementById('dart');
        const aimLine = document.getElementById('aim-line');
        const resultDisplay = document.getElementById('result-display');
        
        const containerRect = container.getBoundingClientRect();
        const centerX = containerRect.width / 2;
        const centerY = containerRect.height - 50; // 다트 발사 시작점 (하단 중앙)

        let isDragging = false;
        let startX, startY;
        let powerX, powerY;

        // --- 마우스 인터랙션 코드 (힘/방향 조절) ---
        container.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX - containerRect.left;
            startY = e.clientY - containerRect.top;

            // 조준선 시작점 설정
            aimLine.style.left = `${centerX}px`;
            aimLine.style.top = `${centerY}px`;
            aimLine.style.display = 'block';
            
            // 다트 숨기기
            dart.style.display = 'none';
            resultDisplay.style.display = 'none';
        });

        container.addEventListener('mousemove', (e) => {
            if (!isDragging) return;

            const currentX = e.clientX - containerRect.left;
            const currentY = e.clientY - containerRect.top;

            // 힘(거리)과 방향(각도) 계산
            const dx = centerX - currentX;
            const dy = centerY - currentY;
            const angle = Math.atan2(dy, dx);
            const distance = Math.min(Math.sqrt(dx * dx + dy * dy), 300); // 최대 힘 제한

            powerX = dx * 0.15; // 힘 계수
            powerY = dy * 0.15;

            // 조준선 업데이트
            aimLine.style.width = `${distance}px`;
            aimLine.style.transform = `rotate(${angle}px)`; // rotate(${angle}rad) 인데 시각적 편의를 위해 dx, dy로

            // 실제로는 반대 방향으로 조준선 그리기
            aimLine.style.transform = `rotate(${Math.atan2(-dy, -dx)}rad)`;
        });

        container.addEventListener('mouseup', (e) => {
            if (!isDragging) return;
            isDragging = false;
            aimLine.style.display = 'none';

            // 다트 발사 시뮬레이션
            launchDart(centerX, centerY, powerX, powerY);
        });

        // --- 다트 발사 물리 시뮬레이션 (JS 애니메이션) ---
        function launchDart(x, y, vx, vy) {
            dart.style.display = 'block';
            let currentX = x;
            let currentY = y;
            let currentVx = vx;
            let currentVy = vy;
            const gravity = 0.5; // 중력
            const friction = 0.99; // 공기 저항

            function animate() {
                currentX += currentVx;
                currentY += currentVy;
                currentVy += gravity; // 중력 적용 (아래로)
                currentVx *= friction;
                currentVy *= friction;

                dart.style.left = `${currentX}px`;
                dart.style.top = `${currentY}px`;

                // 벽에 부딪히거나 바닥에 떨어지면 멈춤
                if (currentX < 0 || currentX > containerRect.width || 
                    currentY < 0 || currentY > containerRect.height) {
                    currentX = Math.max(0, Math.min(containerRect.width, currentX));
                    currentY = Math.max(0, Math.min(containerRect.height, currentY));
                    stopDart(currentX, currentY);
                    return;
                }
                
                // 속도가 매우 느려지면 멈춤
                if (Math.abs(currentVx) < 0.1 && Math.abs(currentVy) < 0.1) {
                     stopDart(currentX, currentY);
                     return;
                }

                requestAnimationFrame(animate);
            }
            animate();
        }

        // --- 다트가 꽂혔을 때 처리 (이펙트, 결과) ---
        function stopDart(x, y) {
            // 1. 이펙트 생성
            const effect = document.createElement('div');
            effect.className = 'impact-effect';
            effect.style.left = `${x}px`;
            effect.style.top = `${y}px`;
            container.appendChild(effect);

            // 2. 이펙트 제거 (애니메이션 후)
            setTimeout(() => effect.remove(), 600);

            // 3. 결과 표시 (간단 지오코딩 클론)
            // 여기서는 실제 API 호출 대신, 좌표에 따라 랜덤 여행지를 매핑해 줍니다.
            const regions = [
                "강원도 강릉시", "제주도 서귀포시", "부산광역시 해운대구", "전라남도 여수시", 
                "경상북도 경주시", "충청남도 태안군", "경기도 가평군", "인천광역시 옹진군"
            ];
            const randomRegion = regions[Math.floor(Math.random() * regions.length)];
            resultDisplay.innerText = `📍 당첨된 여행지: ${randomRegion}`;
            resultDisplay.style.display = 'block';
        }
    </script>
</body>
</html>
"""

# HTML 컴포넌트를 Streamlit에 삽입
components.html(game_html, height=850, scrolling=False)

# --- 사이드바 및 하단 정보 (선택 사항) ---
with st.sidebar:
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSnMGRhuZVQj9_km9qCNSRFsZo_dsevzgUecS-TAg-MjcNbAEsOqYecw-Q&s=10", width=100)
    st.markdown("---")
    st.markdown("### 🎯 게임 방법")
    st.markdown(
        """
        1.  **지도 위**를 마우스로 **클릭**합니다.
        2.  마우스를 클릭한 상태로 **드래그**하여 다트의 **힘**과 **방향**을 조절합니다.
        3.  마우스 버튼을 **떼면**, 다트가 날아갑니다.
        4.  다트가 꽂힌 곳의 여행지가 표시됩니다.
        """
    )
    st.info("실제 '감도 다트' 사이트의 핵심 기능을 본따 만든 클론 프로젝트입니다.")

# 전체 페이지 배경색을 어둡게 (Streamlit 테마 무시)
st.markdown(
    """
    <style>
        .stApp { background-color: #121212; color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)
