import vlc
import time
import os
import threading

library = []

class Node:
    def __init__(self, data):
        self.item = data
        self.next = None
        self.prev = None

class DoublyLinkedList:
    def __init__(self):
        self.start_node = None

    def insert_to_empty_list(self, data):
        if self.start_node is None:
            new_node = Node(data)
            self.start_node = new_node
        else:
            print("The playlist is not empty")

    def insert_to_end(self, data):
        if self.start_node is None:
            self.insert_to_empty_list(data)
            return
        n = self.start_node
        while n.next:
            n = n.next
        new_node = Node(data)
        n.next = new_node
        new_node.prev = n

    def delete_at_end(self):
        if self.start_node is None:
            print("The playlist is empty, no element to delete")
            return
        n = self.start_node
        while n.next:
            n = n.next
        if n.prev:
            n.prev.next = None

class Song:
    def __init__(self, name, file_path):
        self.name = name
        self.file_path = file_path
        self.media = None
        self.event_manager = None

    def play_song(self, end_callback=None):
        if os.path.isfile(self.file_path):
            self.stop_playing_song()
            self.media = vlc.MediaPlayer(self.file_path)
            if end_callback:
                self.event_manager = self.media.event_manager()
                self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, end_callback)
            self.media.play()
            return True
        else:
            print(f"Error: File '{self.file_path}' does not exist.")
            return False

    def stop_playing_song(self):
        if self.media:
            self.media.stop()
            if self.event_manager:
                self.event_manager.event_detach(vlc.EventType.MediaPlayerEndReached)
            self.media.release()

class Playlist:
    def __init__(self, playlist_name):
        self.playlist_name = playlist_name
        self.songs = DoublyLinkedList()
        self.current_node = None
        library.append(self)

    def play_playlist(self):
        if not self.current_node:
            self.current_node = self.songs.start_node
        if self.current_node:
            self.play_current_song()

    def play_current_song(self):
        if self.current_node and os.path.isfile(self.current_node.item.file_path):
            self.current_node.item.play_song(self.song_ended)
            print(f"Now playing: {self.current_node.item.name}")

    def song_ended(self, event):
        if self.current_node.next:
            self.current_node = self.current_node.next
        else:
            self.current_node = None  
        if self.current_node:
            self.play_current_song()
        else:
            print("Playlist finished.")

    def stop_playing_playlist(self):
        if self.current_node and self.current_node.item.media:
            self.current_node.item.stop_playing_song()
        self.current_node = None  

    def skip_to_next_song(self):
        if self.current_node and self.current_node.next:
            self.current_node.item.stop_playing_song()
            self.current_node = self.current_node.next
            self.play_current_song()
            print("Skipped to the next song.")
        else:
            print("No next song to skip to.")  

    def skip_to_previous_song(self):
        if self.current_node and self.current_node.prev:
            self.current_node.item.stop_playing_song()  
            self.current_node = self.current_node.prev  
            self.play_current_song()  
            print("Skipped to the previous song.")
        else:
            print("No previous song to skip to.")  



    def delete_song_from_end_of_playlist(self):
        self.songs.delete_at_end()
        print("Last song in the playlist has been deleted.")





print("Welcome to Brett's Jukebox")
print("Please choose from the following options:")
print("1. Play a song")
print("2. Stop playing Song")
print("3. Create a playlist")
print("4. Rename a playlist")
print("5. Add a Song to a playlist")
print("6. Delete last song from a playlist")
print("7. Play a playlist")
print("8. Stop playing playlist")
print("9. Play the next playlist")
print("10. Play the previous playlist")
print("11. Play the previous song in the current playlist")
print("12. Play the next song in the current playlist")
print("13. Print all available playlists in library")
print("14. Print all songs names on a playlist")
print("15. Delete a playlist")
print("Q. To exit the program")

selection = input('Please enter a menu option or "Q" to quit: ')
current_song = None
current_play_list = None

while selection.lower() != 'q':
    if selection == '1':
        song_name = input('Please enter the name of the song you wish to play: ')
        current_song_path = input('Please enter the file path of the song you wish to play: ')
        current_song = Song(song_name, current_song_path)
        current_song.play_song()
        print("Playing:", song_name)
        
    elif selection == '2':
        if current_song:
            current_song.stop_playing_song()
            print("Stopping the song...")
        else:
            print("No song is currently playing.")
            
    elif selection == '3':
        print("Creating a playlist...")
        playlist_name = input('Please enter the name of the playlist you want to create: ')

        playlist_exists = False
        for playlist in library:
            if playlist.playlist_name.lower() == playlist_name.lower():
                playlist_exists = True
                break

        if playlist_exists:
            print("Playlist already exists. Please use it or select a new name for the playlist.")
        else:
            new_playlist = Playlist(playlist_name)
            library.append(new_playlist)
            print(f"Playlist '{playlist_name}' created successfully.")
        
    elif selection == '4':
        print("Renaming a playlist...")
        change_name = input('Please enter the name of the playlist you want to rename:')
        new_name = input('Please enter the new name for that playlist:')
        
        found = False
        for playlist in library:
            if playlist.playlist_name == change_name:
                playlist.playlist_name = new_name
                print(f"Playlist renamed to '{new_name}'.")
                found = True
                break
        if not found:
            print("Playlist not found.")
            
    elif selection == '5':
        print("Adding a song to a playlist...")
        pick_playlist = input('Please enter the name of the playlist you would like to add a song to:')
        add_song_name = input('Please enter the name of the song you would like to add:')
        add_file_path_song = input('Please enter the filepath of the song you wish to add:')

        if not os.path.isfile(add_file_path_song):
            print("Error: The file does not exist. Please enter a valid file path.")
        else:
            add_song = Song(add_song_name, add_file_path_song)
            playlist_found = False
            for playlist in library:
                if pick_playlist == playlist.playlist_name:
                    playlist.songs.insert_to_end(add_song)
                    print(f"Added song '{add_song_name}' to playlist '{pick_playlist}'.")
                    playlist_found = True
                    break
                
            if not playlist_found:
                print("Playlist does not exist.")
                    
    elif selection == '6':
        print("Deleting a song from the end of a playlist...")
        pick_playlist = input('Please enter the name of the playlist you would like to delete a song from: ')
        playlist_found = False
        
        for playlist in library:
            if playlist.playlist_name == pick_playlist:
                playlist.delete_song_from_end_of_playlist()
                print(f"Last song removed from playlist '{pick_playlist}'.")
                playlist_found = True
                break
                
        if not playlist_found:
            print("Playlist does not exist.")
            
    elif selection == '7':
        print("Playing a playlist...")
        playlist_name = input("Enter the name of the playlist to play: ")
        found = False
        for playlist in library:
            if playlist.playlist_name == playlist_name:
                playlist.play_playlist()
                found = True
                current_playlist = playlist
                break
        if not found:
            print("Playlist does not exist.")
            
    elif selection == '8':
        if current_playlist:  # Check if there is an active playlist
            print(f"Stopping playback of the playlist: {current_playlist.playlist_name}")
            current_playlist.stop_playing_playlist()
        else:
            print("No playlist is currently playing.")
    
    elif selection == '9':
        print("Playing the next playlist...")
        if current_playlist is not None and current_playlist in library:
            current_playlist_index = library.index(current_playlist)
        
       
            if current_playlist_index == len(library) - 1:
                current_playlist_index = 0  
            else:
                current_playlist_index = current_playlist_index + 1
        
            current_playlist = library[current_playlist_index]
            current_playlist.play_playlist()
            print(f"Playing playlist: {current_playlist.playlist_name}")
        
        else:
            print("No current playlist selected or playlist not found in the library.")
           
    elif selection == '10':
        print("Playing the previous playlist...")
        if current_playlist is not None and current_playlist in library:
            current_playlist_index = library.index(current_playlist)

            if current_playlist_index == 0:
                current_playlist_index = len(library) -1
            else:
                current_playlist_index = current_playlist_index - 1

            current_playlist = library[current_playlist_index]
            current_playlist.play_playlist()
            print(f"Playing playlist: {current_playlist.playlist_name}")
        
        else:
            print("No current playlist selected or playlist not found in the library.")
            
    
        
    elif selection == '11':
        print("Playing the previous song in the current playlist...")
        if current_playlist is not None:
            current_playlist.skip_to_previous_song()
        else:
            print("No playlist is currently playing.")
    
    elif selection == '12':
        print("Playing the next song in the current playlist...")
        if current_playlist is not None:
            current_playlist.skip_to_next_song()
        else:
            print("No playlist is currently playing.")

    elif selection == '13':
        if not library:
            print("No playlists are available.")
        else:
            print("Available Playlists:")
            seen_playlists = set()
            for playlist in library:
                if playlist.playlist_name not in seen_playlists:
                    print(playlist.playlist_name)
                    seen_playlists.add(playlist.playlist_name)

    elif selection == '14':
        print("Print songs from a playlist...")
        playlist_name = input("Enter the name of the playlist you want to view songs from: ")

   
        playlist_found = False
        for playlist in library:
            if playlist.playlist_name.lower() == playlist_name.lower():
                playlist_found = True
                if playlist.songs.start_node:  # Check if there are songs in the playlist
                    print(f"Songs in the playlist '{playlist_name}':")
                    node = playlist.songs.start_node
                    while node:
                        print(node.item.name)
                        node = node.next
                else:
                    print("The playlist is empty.")
                break

        if not playlist_found:
            print("Playlist does not exist.")


    elif selection == '15':
        print("Deleting a playlist...")
        playlist_name = input('Please enter the name of the playlist you want to delete: ')
    
        playlist_found = False
        for i, playlist in enumerate(library):
            if playlist.playlist_name.lower() == playlist_name.lower():
                del library[i]
                playlist_found = True
                print(f"Playlist '{playlist_name}' has been deleted.")
                break  # Exit the loop once the playlist is deleted

        if not playlist_found:
            print("Playlist doesn't exist.")
        else:
            print("No playlist selected or the playlist is empty.")

    print(" ")
    print("Welcome to Brett's Jukebox")
    print("Please choose from the following options:")
    print("1. Play a song")
    print("2. Stop playing Song")
    print("3. Create a playlist")
    print("4. Rename a playlist")
    print("5. Add a Song to a playlist")
    print("6. Delete last song from a playlist")
    print("7. Play a playlist")
    print("8. Stop playing playlist")
    print("9. Play the next playlist")
    print("10. Play the previous playlist")
    print("11. Play the previous song in the current playlist")
    print("12. Play the next song in the current playlist")
    print("13. Print all available playlists in library")
    print("14. Print all songs names on a playlist")
    print("15. Delete a playlist")
    print("Q. To exit the program")
    print(" ")

    selection = input('Please enter a menu option or "Q" to quit: ')

print("You have exited Brett's Jukebox.")
print(" ")