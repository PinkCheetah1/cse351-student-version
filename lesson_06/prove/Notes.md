Notes
Process Images in Folder: 
- Check if right extension
- Create input and output paths
- Grab image as item from input path
- Apply processing function to image

I need: 
- Put images to process in Queue (initially in Main?)
- As images get processed, they need to be put in a new queue. 
- All three processing functions need to be running at the same time


What if I use the processing function and just pull out the input/output folder part. Instead, I can create a new function at the start to do that initially. We replace those with the queues, which hold input and output file paths. We don't touch the helper functions. We can still pass in the necessary args for each processer. 

Every processer will take an input queue. But the last one won't take an output queue. So we need a conditional argument in there. And if that argument is None, we skip the load to que phase. 