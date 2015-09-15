reshape_results <- function(results_table = acc[[2]]) {
  ntyper = ncol(results_table)/6
  
  reshaped = matrix(rep(c("reference", "optitype", "bwakit", "hlassign"), each=2), nrow = 1)
  rnames = rownames(results_table)
  
  for (row in 1:nrow(results_table)){
    
    for (i in c(1,3,5)){ #HLA-A B C
      col = sort(union(seq(i, by = 6, length.out = ntyper), seq(i+1, by = 6, length.out = ntyper)))
      #print(paste(row,col))
      reshaped = rbind(reshaped, results_table[row, col])
    }
  }
  
  colnames(reshaped) = make.names(reshaped[1,], unique = T)
  reshaped = tail(reshaped, -1)
  rownames(reshaped) = rep(rnames, each=3)
  return(reshaped)
}

mode <- function(x) {
  ux <- unique(x)
  ux[which.max(tabulate(match(x, ux)))]
}

get_consensus <- function(reshaped_table) {
  for (i in c(3,5,7)){ #cols for typer's allele 1
    reshaped_table = cbind(reshaped_table, paste(reshaped_table[, i], reshaped_table[, (i+1)]))
  } 
  idx = (ncol(reshaped_table)-2):ncol(reshaped_table)
  m = apply(reshaped_table[,idx], MARGIN=1, FUN=mode)
  return(unlist(m))
}


reshaped <- reshape_results()
reshaped = cbind(reshaped, get_consensus(reshaped))