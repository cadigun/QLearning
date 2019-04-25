import time
import random
import collections, math

class Environment(object):
    """A grid world with pellets to collect and an enemy to avoid."""

    def __init__(self, size, density):
        """Environments have fixed size and pellet counts."""
        self.size = size
        self.density = density
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)] # left, down, right, up

    def initialize(self):
        """Place pacman, pellets, and ghost at random locations."""
        
        locations = list()
        for r in range(1,self.size-1):
            for c in range(1,self.size-1):
                locations.append((r, c))
        
        random.shuffle(locations)
        self.pacman = locations.pop()
        
        self.pellets = set()
        for count in range(self.density):
            self.pellets.add(locations.pop())

        self.new_ghost()
        self.next_reward = 0
    
    def new_ghost(self):
        """Place a ghost at one end of pacman's row or column."""
        (r, c) = self.pacman
        locations = [(r, 0), (0, c), (r, self.size-1), (self.size-1, c)]
        choice = random.choice(range(len(locations)))
        self.ghost = locations[choice]
        self.ghost_action = self.directions[choice]
    
    def display(self):
        """Print the environment."""
        for r in range(self.size):
            for c in range(self.size):
                if (r,c) == self.ghost:
                    print 'G',
                elif (r,c) == self.pacman:
                    print 'O',
                elif (r,c) in self.pellets:
                    print '.',
                elif r == 0 or r == self.size-1:
                    print 'X',
                elif c == 0 or c == self.size-1:
                    print 'X',
                else:
                    print ' ',
            print
        print
    
    def actions(self):
        """Return the actions the agent may try to take."""
        if self.terminal():
            return None
        else:
            actualDir = list()
            getXY = ( (self.pacman[0]-1, self.pacman[1]),
                  (self.pacman[0]+1, self.pacman[1]),
                  (self.pacman[0], self.pacman[1]+1),
                  (self.pacman[0], self.pacman[1]+1),
                 )
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

            for i in range(len(getXY)):
                r = getXY[i][0]
                c = getXY[i][1]
                if (r == 0 or r >= self.size-1 or c == 0 or c >= self.size-1):
                    pass
                else:
                        actualDir.append(directions[i])
            return actualDir

    def terminal(self):
        """Return whether the episode is over."""
        if self.next_reward == -100:
            return True
        elif len(self.pellets) == 0:
            return True
        else:
            return False
    
    def reward(self):
        """Return the reward earned at during the last update."""
        return self.next_reward
        
    def update(self, action):
        """Adjust the environment given the agent's choice of action."""
        
        pacman = self.pacman
        ghost = self.ghost
        
        # Pacman moves as chosen
        (r, c) = self.pacman
        (dr, dc) = action
        self.pacman = (r+dr, c+dc)
        
        # Ghost moves in its direction
        (r, c) = self.ghost
        (dr, dc) = self.ghost_action
        self.ghost = (r+dr, c+dc)
        
        # Ghost is replaced when it leaves
        (r, c) = self.ghost
        if r == 0 or r == self.size-1:
            self.new_ghost()
        elif c == 0 or c == self.size-1:
            self.new_ghost()
        
        (r,c) = self.pacman
        (gr,gc) = self.ghost
        
        # Negative reward for hitting the ghost
        if self.pacman == self.ghost:
            self.next_reward = -100
        elif (pacman, ghost) == (self.ghost, self.pacman):
            self.next_reward = -100
        
        # Negative reward for hitting a wall
        elif r == 0 or r == self.size-1:
            self.next_reward = -100
        elif c == 0 or c == self.size-1:
            self.next_reward = -100
        
        # Positive reward for consuming a pellet
        elif self.pacman in self.pellets:
            self.next_reward = 10
            self.pellets.remove(self.pacman)
        else:
            self.next_reward = 0

    def state(self):
        """Return a description of the state of the environment."""
        s = dict()
        
        # Baseline feature noting how many pellets are left
        s['pellets left'] = len(self.pellets) / float(self.density)
        
        # YOU ADD MORE FEATURES

        """
        Some more features for Pacman Agent include:
        - position of the next pellet ['next pellet']
        - position from ghost and chances of escape ['escape ghost']
        - position from wall ['avoid wall']

        """

        def getFuncPellet(agentPosition, listOfPellets):
            if ([] not in listOfPellets):
                valueList = list()
                
                for nextPellet in listOfPellets:
                    distance = abs(self.pacman[0] - nextPellet[0]) + abs(self.pacman[1] - nextPellet[1])
                    valueList.append(distance)
                
                maxValue = valueList[0] # give nearest food pellet highest value
                for i in range(1, len(valueList)):
                    if (valueList[i] > maxValue):
                        maxValue = valueList[i]
                value = math.exp(1/maxValue)/maxValue
                return value
            
        survival = abs(self.pacman[0] - self.ghost[0]) + abs(self.pacman[1] - self.ghost[1])
        
        s['escape ghost'] = 0.0
        s['next pellet'] = getFuncPellet(self.pacman, list(self.pellets))
        s['avoid wall'] = 1.0

        getXY = ( (self.pacman[0]-1, self.pacman[1]),
                  (self.pacman[0]+1, self.pacman[1]),
                  (self.pacman[0], self.pacman[1]+1),
                  (self.pacman[0], self.pacman[1]+1),
                 )

        walls = list()
        for i in range(len(getXY)):
            r = getXY[i][0]
            c = getXY[i][1]
            if (r == 0 or r == self.size-1 or c == 0 or c == self.size-1):
                walls.append('X')

        if 'X' in walls:
            s['avoid wall'] = 0.0
        
        if (survival >= 2) and (survival <= 5):
            s['escape ghost'] = 1.0

        elif (survival > 5):
            s['escape ghost'] = 1.5
        else:
            pass


        if (survival < 3) and ('X' in walls):
            s['avoid wall'] =  -2.0 # -1.0

        elif(survival < 3):
        	s['escape ghost'] = 0.0 #0.0

        elif('X' in walls) and (survival > 3):
        	s['avoid wall'] = -1.5 #-1.0
            
        return s

class Agent(object):
    """Learns to act within the environment."""

    def __init__(self):
        """Establish initial weights and learning parameters."""
        self.w = collections.defaultdict(float) # Each w((f,a)) starts at 0
        self.epsilon = 0.05 # Exploration rate
        self.gamma = 0.99 # Discount factor
        self.alpha = 0.01 # Learning rate

    def choose(self, s, actions):
        """Return an action to try in this state."""
        p = random.random()
        if p < self.epsilon:
            return random.choice(actions)
        else:
            return self.policy(s, actions)

    def policy(self, s, actions):
        """Return the best action for this state."""
        max_value = max([self.Q(s,a) for a in actions])
        max_actions = [a for a in actions if self.Q(s,a) == max_value]
        return random.choice(max_actions)

    def Q(self, s, a):
        """Return the estimated Q-value of this action in this state."""

        # YOU CHANGE THIS
        qValue = 0.0
        for f in s:
            qValue = qValue + ( self.w[f] * s[f] )
        return qValue
    
    def observe(self, s, a, sp, r, actions):
        """Update weights based on this observed step."""

        # YOU FILL THIS IN
        change = (r + self.gamma * self.policy(sp, a)) - self.policy(s,a)
        for f in s.keys():
            self.w[f] += self.alpha * change * s[f]
        

def main():
    """Train an agent and then watch it act."""
    global environment
    
    environment = Environment(20,10)
    agent = Agent()

    for episode in range(1000):
        environment.initialize()
        while not environment.terminal():
            
            s = environment.state()
            actions = environment.actions()
            a = agent.choose(s, actions)
            environment.update(a)
            
            sp = environment.state()
            r = environment.reward()
            actions = environment.actions()
            agent.observe(s, a, sp, r, actions)

    environment.initialize()
    environment.display()
    while not environment.terminal():
        
        s = environment.state()
        actions = environment.actions()
        a = agent.policy(s, actions)
        
        environment.update(a)
        time.sleep(0.25)

        environment.display()

if __name__ == '__main__':
    main()
