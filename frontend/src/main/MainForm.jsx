import React, { useRef, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js'; // 명암과 선명도 향상에 도움을 줄 수 있습니다.

import { UserContext } from '../UserContext';

import chatbot from '../static/img/chatbot.svg';
import { SEOMetaTag } from '../snippets';

function MainForm() {

    const canvasRef = useRef();
    let rotationDirection = 0.000005; // 초기 회전 방향
    let lastDirectionChangeTime = Date.now();

    const { user } = useContext(UserContext);
    useEffect(() => {
        window.scrollTo(0, 0);
    }, [user]);

    useEffect(() => {
        const scene = new THREE.Scene();
        const canvas = canvasRef.current;
        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        //renderer.outputColorSpace = THREE.ColorSpace.sRGB;

        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100);
        camera.position.set(0, 0, 90);

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.25;
        controls.enableZoom = true;
        controls.autoRotate = false;
        controls.autoRotateSpeed = 0.05;

        scene.background = new THREE.Color('#191919');
        const group = new THREE.Group();

        const composer = new EffectComposer(renderer);
        composer.addPass(new RenderPass(scene, camera));
        const unrealBloom = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 1.5, 0.4, 0.85);
        composer.addPass(unrealBloom);

        // 환경 조명 추가
        const ambientLight = new THREE.AmbientLight(0xffffff, 1);
        scene.add(ambientLight);

        // 방향 조명 추가
        const directionalLight = new THREE.DirectionalLight(0xE75690, 5);
        directionalLight.position.set(10, 10, 10);
        scene.add(directionalLight);

        const hemisphereLight = new THREE.HemisphereLight(0xE75690, 0x080820, 1);
        scene.add(hemisphereLight);

        // GLTFLoader를 사용하여 모델 로드
        const loader = new GLTFLoader();
        loader.load(
            process.env.PUBLIC_URL + '/model/littlePrince/scene.gltf',
            (gltf) => {
                gltf.scene.traverse((object) => {
                    if (object.isMesh && object.material) {
                        object.material.transparent = true;
                        object.material.opacity = 1.2;
                    }
                });
                gltf.scene.rotation.x = Math.PI / 8;
                gltf.scene.rotation.y -= Math.PI / 4;
                gltf.scene.position.y -= 70.5;
                gltf.scene.position.z -= 100;
                //scene.add(gltf.scene);
                group.add(gltf.scene);
            },
            undefined,
            (error) => {
              console.error('An error happened', error);
            }
        );
        group.position.set(0, 6, 60);
        scene.add(group);

        let animationFrameId; // 애니메이션 프레임 ID를 저장할 변수
        function animate() {
            animationFrameId = requestAnimationFrame(animate);
            const currentTime = Date.now();
            if (currentTime - lastDirectionChangeTime > 6000) { // 5초마다 회전 방향 변경
                rotationDirection *= -1; // 회전 방향 반대로 변경
                lastDirectionChangeTime = currentTime;
            }
            controls.update();
            group.rotation.z += rotationDirection; 
            composer.render();
        }

        animate();

        return () => {
            cancelAnimationFrame(animationFrameId);
            scene.clear();
            scene.traverse(function (object) {
                if (object.isMesh) {
                    if (object.geometry) {
                        object.geometry.dispose();
                    }
                    if (object.material) {
                        if (object.material instanceof Array) {
                            object.material.forEach(material => material.dispose());
                        } else {
                            object.material.dispose();
                        }
                    }
                }
            });
            renderer.dispose();
            controls.dispose();
        };
    }, []);

    return (
        <div className='main-container'>
            <SEOMetaTag 
                title='몽글몽글: 랜덤채팅'
                description='대학생 커뮤니티 몽글몽글에서 다른 학교의 친구들을 만나보세요. 본인과 상대방의 대학교가 공개됩니다. 대학생들의 공간에서 더 안전하게 대화하세요!'
                keywords='몽글몽글, mongle, 랜덤채팅, 커뮤니티'
                image='https://mongles.com/og_image.png'
                url='https://mongles.com/'
            />
            <canvas ref={canvasRef} />
            <div className='rendered-name'>
                <p className='mongle'>Mongle</p>
                <p className='para'>다른 학교의 친구들을 만나보세요</p>
                <Link to="/chat" className="start">
                    <p className='start-p'>시작하기</p>
                </Link>
            </div>
            <div className='chatbot'>
                <a href="http://pf.kakao.com/_fYEaG/chat"
                    target='_blank'
                    rel='noreferrer noopener'
                >
                    <img src={chatbot} alt="chatbot" />
                </a>
            </div>
        </div>
    );
}

export default MainForm;
