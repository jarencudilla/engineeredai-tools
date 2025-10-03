<?php
/**
 * The template for displaying 404 pages (not found)
 *
 * @package QAJourney
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found | <?php bloginfo('name'); ?></title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            color: #2c3e50;
        }

        .container {
            background: white;
            border-radius: 12px;
            padding: 60px 40px;
            max-width: 850px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            text-align: center;
        }

        .error-code {
            font-size: 100px;
            font-weight: 900;
            color: #e74c3c;
            line-height: 1;
            margin-bottom: 15px;
            letter-spacing: -5px;
            text-shadow: 3px 3px 0px rgba(0,0,0,0.1);
        }

        h1 {
            font-size: 28px;
            color: #2c3e50;
            margin-bottom: 15px;
            font-weight: 700;
        }

        .message {
            font-size: 16px;
            color: #546e7a;
            margin-bottom: 30px;
            line-height: 1.7;
        }

        #gameCanvas {
            width: 100%;
            height: 400px;
            background: linear-gradient(to bottom, #e8f4f8 0%, #d4e9f0 100%);
            border-radius: 8px;
            margin: 20px 0;
            cursor: crosshair;
            display: block;
            border: 3px solid #3498db;
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);
        }

        .game-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            font-size: 14px;
            color: #546e7a;
            flex-wrap: wrap;
            gap: 10px;
        }

        .score {
            font-size: 22px;
            font-weight: bold;
            color: #e74c3c;
        }

        .timer {
            font-size: 20px;
            font-weight: bold;
            color: #3498db;
        }

        .high-score {
            font-size: 16px;
            color: #27ae60;
            font-weight: 600;
        }

        .instruction {
            font-size: 14px;
            color: #888;
            margin-bottom: 20px;
            font-style: italic;
        }

        .bug-legend {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 15px;
            margin: 20px 0;
            font-size: 12px;
        }

        .bug-type {
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .bug-color {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid #333;
        }

        .links {
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 30px;
        }

        .btn {
            display: inline-block;
            padding: 12px 28px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 15px;
            transition: all 0.3s ease;
            letter-spacing: 0.3px;
        }

        .btn-primary {
            background: #2c3e50;
            color: white;
        }

        .btn-primary:hover {
            background: #1a252f;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(44, 62, 80, 0.25);
        }

        .btn-secondary {
            background: white;
            color: #2c3e50;
            border: 2px solid #2c3e50;
        }

        .btn-secondary:hover {
            background: #2c3e50;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(44, 62, 80, 0.2);
        }

        @media (max-width: 600px) {
            .container {
                padding: 40px 25px;
            }

            .error-code {
                font-size: 80px;
            }

            h1 {
                font-size: 24px;
            }

            .message {
                font-size: 15px;
            }

            #gameCanvas {
                height: 350px;
            }

            .game-info {
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-code">404</div>
        <h1>🐛 Critical Bug Detected!</h1>
        <p class="message">
            Uh oh! Looks like our QA team missed this one. Help us squash these bugs before they crash production! Different bugs have different behaviors - can you catch them all?
        </p>
        
        <div class="game-info">
            <div class="timer">⏱️ Time: <span id="timer">45</span>s</div>
            <div class="score">🎯 Score: <span id="score">0</span></div>
            <div class="high-score">🏆 Best: <span id="highScore">0</span></div>
        </div>
        
        <div class="bug-legend">
            <div class="bug-type"><div class="bug-color" style="background:#e74c3c"></div><span>NullPointer (1pt)</span></div>
            <div class="bug-type"><div class="bug-color" style="background:#e67e22"></div><span>SyntaxError (2pt)</span></div>
            <div class="bug-type"><div class="bug-color" style="background:#9b59b6"></div><span>MemoryLeak (3pt)</span></div>
            <div class="bug-type"><div class="bug-color" style="background:#3498db"></div><span>RaceCondition (4pt)</span></div>
            <div class="bug-type"><div class="bug-color" style="background:#2ecc71"></div><span>InfiniteLoop (2pt)</span></div>
            <div class="bug-type"><div class="bug-color" style="background:#95a5a6"></div><span>404Bug (5pt)</span></div>
        </div>
        
        <div class="instruction">Click the bugs to squash them! Harder bugs = more points 🎮</div>
        
        <canvas id="gameCanvas"></canvas>
        
        <div class="links">
            <a href="<?php echo esc_url(home_url('/')); ?>" class="btn btn-primary">Go Home</a>
            <a href="<?php echo esc_url(home_url('/blog')); ?>" class="btn btn-secondary">Browse Blog</a>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        // Set canvas size
        function resizeCanvas() {
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        // Game variables
        let bugs = [];
        let particles = [];
        let score = 0;
        let highScore = 0;
        let timeLeft = 45;
        let gameActive = false;
        let gameOver = false;
        let bugSpeed = 1200;
        let maxBugs = 6;
        let spawnInterval;
        let timerInterval;

        // Bug types configuration
        const bugTypes = {
            nullPointer: {
                name: 'NullPointer',
                color: '#e74c3c',
                points: 1,
                lifetime: 2500,
                weight: 30
            },
            syntaxError: {
                name: 'SyntaxError',
                color: '#e67e22',
                points: 2,
                lifetime: 2200,
                weight: 25,
                wobble: true
            },
            memoryLeak: {
                name: 'MemoryLeak',
                color: '#9b59b6',
                points: 3,
                lifetime: 2800,
                weight: 20,
                grows: true
            },
            raceCondition: {
                name: 'RaceCondition',
                color: '#3498db',
                points: 4,
                lifetime: 1800,
                weight: 12,
                teleports: true
            },
            infiniteLoop: {
                name: 'InfiniteLoop',
                color: '#2ecc71',
                points: 2,
                lifetime: 2500,
                weight: 10,
                spins: true
            },
            bug404: {
                name: '404Bug',
                color: '#95a5a6',
                points: 5,
                lifetime: 1500,
                weight: 3,
                blinks: true
            }
        };

        // Particle class for effects
        class Particle {
            constructor(x, y, color) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 8;
                this.vy = (Math.random() - 0.5) * 8;
                this.life = 1;
                this.decay = 0.02;
                this.size = Math.random() * 6 + 3;
                this.color = color;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;
                this.vy += 0.3; // gravity
                this.life -= this.decay;
            }

            draw() {
                ctx.globalAlpha = this.life;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
            }
        }

        // Bug class
        class Bug {
            constructor() {
                // Select bug type based on weights
                const type = this.selectBugType();
                this.type = bugTypes[type];
                
                this.size = 45;
                this.baseSize = 45;
                this.x = Math.random() * (canvas.width - this.size);
                this.y = Math.random() * (canvas.height - this.size);
                this.alive = true;
                this.lifetime = 0;
                this.visible = true;
                this.rotation = 0;
                this.wobbleOffset = 0;
                this.teleportTimer = 0;
                this.blinkTimer = 0;
            }

            selectBugType() {
                const totalWeight = Object.values(bugTypes).reduce((sum, type) => sum + type.weight, 0);
                let random = Math.random() * totalWeight;
                
                for (let [key, type] of Object.entries(bugTypes)) {
                    random -= type.weight;
                    if (random <= 0) return key;
                }
                return 'nullPointer';
            }

            draw() {
                if (!this.alive || !this.visible) return;

                ctx.save();
                
                // Apply transformations based on bug type
                let drawX = this.x + this.size/2;
                let drawY = this.y + this.size/2;
                
                if (this.type.wobble) {
                    drawX += Math.sin(this.wobbleOffset) * 10;
                }
                
                ctx.translate(drawX, drawY);
                if (this.type.spins) {
                    ctx.rotate(this.rotation);
                }
                
                // Shadow
                ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
                ctx.beginPath();
                ctx.ellipse(5, this.size/2 + 5, this.size/2.5, this.size/6, 0, 0, Math.PI * 2);
                ctx.fill();

                // Bug body
                ctx.fillStyle = this.type.color;
                ctx.beginPath();
                ctx.ellipse(0, 0, this.size/2, this.size/3, 0, 0, Math.PI * 2);
                ctx.fill();

                // Bug head
                ctx.beginPath();
                ctx.arc(0, -this.size/4, this.size/3.5, 0, Math.PI * 2);
                ctx.fill();

                // Antennae
                ctx.strokeStyle = this.type.color;
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(-8, -this.size/3);
                ctx.lineTo(-12, -this.size/2);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(8, -this.size/3);
                ctx.lineTo(12, -this.size/2);
                ctx.stroke();
                
                // Antennae tips
                ctx.fillStyle = this.type.color;
                ctx.beginPath();
                ctx.arc(-12, -this.size/2, 3, 0, Math.PI * 2);
                ctx.arc(12, -this.size/2, 3, 0, Math.PI * 2);
                ctx.fill();

                // Eyes
                ctx.fillStyle = '#fff';
                ctx.beginPath();
                ctx.arc(-7, -this.size/4, 4, 0, Math.PI * 2);
                ctx.arc(7, -this.size/4, 4, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = '#000';
                ctx.beginPath();
                ctx.arc(-7, -this.size/4, 2, 0, Math.PI * 2);
                ctx.arc(7, -this.size/4, 2, 0, Math.PI * 2);
                ctx.fill();

                // Legs
                ctx.strokeStyle = this.type.color;
                ctx.lineWidth = 2;
                for (let i = 0; i < 3; i++) {
                    const legAngle = (i - 1) * 0.4;
                    ctx.beginPath();
                    ctx.moveTo(Math.sin(legAngle) * this.size/3, this.size/4);
                    ctx.lineTo(Math.sin(legAngle) * this.size/2, this.size/2 + 8);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(Math.sin(legAngle) * this.size/3, this.size/4);
                    ctx.lineTo(Math.sin(legAngle) * this.size/2, this.size/2 + 8);
                    ctx.stroke();
                }

                ctx.restore();

                // Draw bug type label
                ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
                ctx.font = 'bold 10px monospace';
                ctx.textAlign = 'center';
                ctx.fillText(this.type.name, this.x + this.size/2, this.y - 5);
            }

            update(deltaTime) {
                this.lifetime += deltaTime;
                
                // Type-specific behaviors
                if (this.type.wobble) {
                    this.wobbleOffset += deltaTime * 0.005;
                }
                
                if (this.type.grows) {
                    this.size = this.baseSize + Math.sin(this.lifetime * 0.002) * 10;
                }
                
                if (this.type.spins) {
                    this.rotation += deltaTime * 0.003;
                }
                
                if (this.type.teleports) {
                    this.teleportTimer += deltaTime;
                    if (this.teleportTimer > 800) {
                        this.x = Math.random() * (canvas.width - this.size);
                        this.y = Math.random() * (canvas.height - this.size);
                        this.teleportTimer = 0;
                    }
                }
                
                if (this.type.blinks) {
                    this.blinkTimer += deltaTime;
                    if (this.blinkTimer > 300) {
                        this.visible = !this.visible;
                        this.blinkTimer = 0;
                    }
                }

                if (this.lifetime >= this.type.lifetime) {
                    this.alive = false;
                }
            }

            contains(x, y) {
                if (!this.visible) return false;
                const centerX = this.x + this.size/2;
                const centerY = this.y + this.size/2;
                const distance = Math.sqrt((x - centerX) ** 2 + (y - centerY) ** 2);
                return distance <= this.size/2;
            }

            squash() {
                this.alive = false;
                
                // Create particle explosion
                for (let i = 0; i < 15; i++) {
                    particles.push(new Particle(
                        this.x + this.size/2,
                        this.y + this.size/2,
                        this.type.color
                    ));
                }
                
                return this.type.points;
            }
        }

        // Spawn bug
        function spawnBug() {
            if (bugs.filter(b => b.alive).length < maxBugs && gameActive) {
                bugs.push(new Bug());
            }
        }

        // Start game
        function startGame() {
            gameActive = true;
            gameOver = false;
            score = 0;
            timeLeft = 45;
            bugs = [];
            particles = [];
            bugSpeed = 1200;
            document.getElementById('score').textContent = '0';
            document.getElementById('timer').textContent = '45';

            spawnInterval = setInterval(spawnBug, bugSpeed);

            timerInterval = setInterval(() => {
                timeLeft--;
                document.getElementById('timer').textContent = timeLeft;
                
                if (timeLeft <= 0) {
                    endGame();
                }
            }, 1000);
        }

        // End game
        function endGame() {
            gameActive = false;
            gameOver = true;
            clearInterval(spawnInterval);
            clearInterval(timerInterval);
            
            if (score > highScore) {
                highScore = score;
                document.getElementById('highScore').textContent = highScore;
            }
        }

        // Handle click
        function handleClick(x, y) {
            if (!gameActive && !gameOver) {
                startGame();
                return;
            }

            if (gameOver) {
                startGame();
                return;
            }

            // Check if clicked on a bug
            for (let bug of bugs) {
                if (bug.alive && bug.contains(x, y)) {
                    const points = bug.squash();
                    score += points;
                    document.getElementById('score').textContent = score;
                    
                    // Speed up game every 10 points
                    if (score % 10 === 0 && bugSpeed > 400) {
                        bugSpeed -= 150;
                        clearInterval(spawnInterval);
                        spawnInterval = setInterval(spawnBug, bugSpeed);
                    }
                    break;
                }
            }
        }

        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            handleClick(x, y);
        });

        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const touch = e.touches[0];
            const x = touch.clientX - rect.left;
            const y = touch.clientY - rect.top;
            handleClick(x, y);
        });

        // Game loop
        let lastTime = 0;
        function gameLoop(timestamp) {
            const deltaTime = timestamp - lastTime;
            lastTime = timestamp;

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Update and draw particles
            particles.forEach((particle, index) => {
                particle.update();
                particle.draw();
                if (particle.life <= 0) {
                    particles.splice(index, 1);
                }
            });

            // Update and draw bugs
            bugs.forEach(bug => {
                if (gameActive) {
                    bug.update(deltaTime);
                }
                bug.draw();
            });

            bugs = bugs.filter(b => b.alive);

            // Draw start message
            if (!gameActive && !gameOver) {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#fff';
                ctx.font = 'bold 28px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('Click to Start Bug Hunt!', canvas.width / 2, canvas.height / 2);
                ctx.font = '16px Arial';
                ctx.fillText('Catch different bugs for different points', canvas.width / 2, canvas.height / 2 + 35);
            }

            // Draw game over
            if (gameOver) {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#fff';
                ctx.font = 'bold 36px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('Time\'s Up!', canvas.width / 2, canvas.height / 2 - 50);
                ctx.font = '24px Arial';
                ctx.fillText('Final Score: ' + score, canvas.width / 2, canvas.height / 2);
                
                if (score === highScore && score > 0) {
                    ctx.fillStyle = '#f39c12';
                    ctx.font = 'bold 20px Arial';
                    ctx.fillText('🎉 NEW HIGH SCORE! 🎉', canvas.width / 2, canvas.height / 2 + 40);
                }
                
                ctx.fillStyle = '#fff';
                ctx.font = '16px Arial';
                ctx.fillText('Click to play again', canvas.width / 2, canvas.height / 2 + 80);
            }

            requestAnimationFrame(gameLoop);
        }

        gameLoop(0);
    </script>
</body>
</html>