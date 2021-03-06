#!/usr/bin/env python
# coding: utf-8

# In[1]:


from Game import *


# ## Rules of the Game

# In[2]:


def initial_state():
    board=Board(3,3)
    board.pieces=['.','X','O']
    return board

def show_state(state):
    print(state)
    
def valid_moves(state,player):  # returns a list of all of the possible moves given a state
    moves=[]
    
    for i in range(9):
        if state[i]==0:
            moves.append(i)
    
    return moves
    
def update_state(state,player,move):
    
    new_state=state
    state[move]=player
    
    return new_state

def win_status(state,player):
    # "win" if the player wins
    # "lose" if the player loses
    # "stalemate" if a tie
    # None if the game continues
    
    # 0 1 2
    # 3 4 5
    # 6 7 8
    
    if state[0]==player and state[1]==player and state[2]==player:
        return "win"
    if state[3]==player and state[4]==player and state[5]==player:
        return "win"
    if state[6]==player and state[7]==player and state[8]==player:
        return "win"
    if state[0]==player and state[3]==player and state[6]==player:
        return "win"
    if state[1]==player and state[4]==player and state[7]==player:
        return "win"
    if state[2]==player and state[5]==player and state[8]==player:
        return "win"
    if state[0]==player and state[4]==player and state[8]==player:
        return "win"
    if state[6]==player and state[4]==player and state[2]==player:
        return "win"
    
    if player==1:
        other_player=2
    else:
        other_player=1
        
        
    if not valid_moves(state,other_player):
        return "stalemate"
    
    
    return None
    


# ## Agents

# In[3]:


def human_move(state,player):
    print("""
     0 1 2
     3 4 5
     6 7 8
    """)
    
    move=int(input("What move?"))
    
    return move

human_agent=Agent(human_move)


# In[4]:


def random_move(state,player):
    possible_moves=valid_moves(state,player)
    move=random.choice(possible_moves)
    return move


random_agent=Agent(random_move)


# In[12]:


from Game.minimax import *
def minimax_move(state,player):

    values,moves=minimax_values(state,player,display=False)
    return top_choice(moves,values)


minimax_agent=Agent(minimax_move)


# In[6]:


def skittles_move(state,player,info):
    S=info.S
    last_action=info.last_action
    last_state=info.last_state
    
    
    # if Ive never seen this state before
    if not state in S:
        actions=valid_moves(state,player)

        S[state]=Table()
        for action in actions:
            S[state][action]=3     
    
    move=weighted_choice(S[state])  # weighted across actions
    
    # what if there are no skittles for a particular state?
    # move is None in that case
    
    if move is None:
        # learn a little bit
        if last_state:
            S[last_state][last_action]=S[last_state][last_action]-1
            if S[last_state][last_action]<0:
                S[last_state][last_action]=0
        
        move=random_move(state,player)
    
    return move

def skittles_after(status,player,info):
    S=info.S
    last_action=info.last_action
    last_state=info.last_state

    if status=='lose':
        # learn a little bit
        S[last_state][last_action]=S[last_state][last_action]-1
        if S[last_state][last_action]<0:
            S[last_state][last_action]=0
        
    


skittles_agent=Agent(skittles_move)
skittles_agent.S=Table()
skittles_agent.post=skittles_after


skittles_agent2=Agent(skittles_move)
skittles_agent2.S=Table()
skittles_agent2.post=skittles_after


# In[7]:


def Q_move(state,player,info):
    Q=info.Q
    last_action=info.last_action
    last_state=info.last_state
    
    α=info.α
    γ=info.γ
    ϵ=info.ϵ
    

    # if Ive never seen this state before
    if not state in Q:
        actions=valid_moves(state,player)

        Q[state]=Table()
        for action in actions:
            Q[state][action]=0     
    
    # deal with random vs top choice here
    if random.random()<ϵ:
        move=random_move(state,player)  
    else:
        move=top_choice(Q[state]) 
    
    # what if there are no skittles for a particular state?
    # move is None in that case
    
    if not last_action is None:  # not the first move
        # learn a little bit
        # change equation here
        reward=0
        
        # Bellman equation
        Q[last_state][last_action] += α*(reward+
                         γ*max([Q[state][a] for a in Q[state]])  - 
                                Q[last_state][last_action])
    
        
    
    return move

def Q_after(status,player,info):
    Q=info.Q
    last_action=info.last_action
    last_state=info.last_state

    α=info.α
    γ=info.γ
    ϵ=info.ϵ
    
    if status=='lose':
        reward=-1
    elif status=='win':
        reward=1
    elif status=='stalemate':
        reward=0.5
    else:
        reward=0
        
    # learn a little bit
    Q[last_state][last_action] += α*(reward-Q[last_state][last_action])
        


# In[15]:


Q1_agent=Agent(Q_move)
Q1_agent.Q=LoadTable('Q1_TTT_data.json')
Q1_agent.post=Q_after

Q1_agent.α=0.3  # learning rate
Q1_agent.γ=0.9  # memory constant, discount factor
Q1_agent.ϵ=0.1  # probability of a random move during learning

Q2_agent=Agent(Q_move)
Q2_agent.Q=LoadTable('Q2_TTT_data.json')
Q2_agent.post=Q_after

Q2_agent.α=0.3  # learning rate
Q2_agent.γ=0.9  # memory constant, discount factor
Q2_agent.ϵ=0.1  # probability of a random move during learning


# In[23]:


total_number_of_games=0
for epoch in range(100):
    
    number_training_games=1000
    number_of_testing_games=10
    
    #=================
    # traning cycle
    Q1_agent.α=0.3  # learning rate
    Q1_agent.ϵ=0.1  # probability of a random move during learning
    Q2_agent.α=0.3  # learning rate
    Q2_agent.ϵ=0.1  # probability of a random move during learning
    
    g=Game(number_training_games)
    g.display=False
    g.run(Q1_agent,Q2_agent)

    #=================
    # testing cycle
    Q1_agent.α=0.0  # learning rate
    Q1_agent.ϵ=0.0  # probability of a random move during learning
    Q2_agent.α=0.0  # learning rate
    Q2_agent.ϵ=0.0  # probability of a random move during learning
    
    
    g=Game(number_of_testing_games)
    g.display=False
    result=g.run(Q1_agent,Q2_agent)
    
    total_number_of_games+=number_training_games
    win_percentage=sum([r==1 for r in result])/number_training_games*100
    loss_percentage=sum([r==2 for r in result])/number_training_games*100
    tie_percentage=sum([r==0 for r in result])/number_training_games*100

    print(total_number_of_games,":",win_percentage," ",end="")
    
    SaveTable(Q1_agent.Q,'Q1_TTT_data.json')
    SaveTable(Q2_agent.Q,'Q2_TTT_data.json')    
    


# In[24]:


g=Game(number_of_testing_games)
g.display=False
result=g.run(minimax_agent,Q2_agent)


# In[25]:


g.report()


# In[26]:


g=Game(number_of_testing_games)
g.display=False
result=g.run(Q1_agent,minimax_agent)


# In[27]:


g.report()


# ## After 100,000 games, 
# 
# 1. ties 100% with minimax
# 2. I defeated it with the game below:
# 
#     Game  1
#      .  .  . 
#      .  .  . 
#      .  .  . 
# 
# 
#          0 1 2
#          3 4 5
#          6 7 8
# 
#     What move? 4
#     Player 1 moves 4
#      .  .  . 
#      .  X  . 
#      .  .  . 
# 
#     Player 2 moves 0
#      O  .  . 
#      .  X  . 
#      .  .  . 
# 
# 
#          0 1 2
#          3 4 5
#          6 7 8
# 
#     What move? 1
#     Player 1 moves 1
#      O  X  . 
#      .  X  . 
#      .  .  . 
# 
#     Player 2 moves 7
#      O  X  . 
#      .  X  . 
#      .  O  . 
# 
# 
#          0 1 2
#          3 4 5
#          6 7 8
# 
#     What move? 6
#     Player 1 moves 6
#      O  X  . 
#      .  X  . 
#      X  O  . 
# 
#     Player 2 moves 3
#      O  X  . 
#      O  X  . 
#      X  O  . 
# 
# 
#          0 1 2
#          3 4 5
#          6 7 8
# 
#     What move? 2
#     Player 1 moves 2
#      O  X  X 
#      O  X  . 
#      X  O  . 
# 
#     Player  1 won.

# In[28]:


g=Game(1)
result=g.run(human_agent,Q2_agent)


# In[ ]:




